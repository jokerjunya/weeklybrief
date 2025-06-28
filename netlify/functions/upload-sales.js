/**
 * Netlify Function: 売上データアップロード処理
 * 
 * CSV売上データを受け取り、Enhanced DeepResearchで処理
 */

const formidable = require('formidable');
const csv = require('csv-parser');
const fs = require('fs');

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers,
            body: JSON.stringify({ error: 'Method Not Allowed' })
        };
    }

    try {
        // リクエストボディからCSVデータを取得
        const requestData = JSON.parse(event.body);
        const csvData = requestData.csvData;
        const filename = requestData.filename || 'upload.csv';

        if (!csvData) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ error: 'CSVデータが見つかりません' })
            };
        }

        // CSVデータの解析
        const parsedData = await parseCSVData(csvData);
        
        // データ検証
        const validation = validateSalesData(parsedData);
        if (!validation.isValid) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({ 
                    error: 'データ検証エラー',
                    validationErrors: validation.errors
                })
            };
        }

        // Enhanced DeepResearch で売上データを分析
        const analysisResult = await analyzeSalesData(parsedData);

        // データ保存（簡易版、実際はDBに保存）
        const savedData = await saveSalesData(parsedData, analysisResult);

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify({
                status: 'uploaded',
                data_summary: {
                    filename: filename,
                    rows: parsedData.length,
                    columns: Object.keys(parsedData[0] || {}).length,
                    upload_time: new Date().toISOString()
                },
                analysis: analysisResult,
                saved_id: savedData.id
            })
        };

    } catch (error) {
        console.error('Sales Upload Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: '売上データアップロードエラー',
                message: error.message
            })
        };
    }
};

/**
 * CSVデータをパース
 */
async function parseCSVData(csvString) {
    return new Promise((resolve, reject) => {
        const results = [];
        const lines = csvString.split('\n');
        
        if (lines.length < 2) {
            reject(new Error('CSVデータが不完全です'));
            return;
        }

        const headers = lines[0].split(',').map(h => h.trim());
        
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            const values = line.split(',').map(v => v.trim());
            const row = {};
            
            headers.forEach((header, index) => {
                row[header] = values[index] || '';
            });
            
            results.push(row);
        }
        
        resolve(results);
    });
}

/**
 * 売上データの検証
 */
function validateSalesData(data) {
    const errors = [];
    
    if (!Array.isArray(data) || data.length === 0) {
        errors.push('データが空です');
        return { isValid: false, errors };
    }

    // 必要な列の確認
    const requiredColumns = ['日付', '売上額', '商品名'];
    const firstRow = data[0];
    const columns = Object.keys(firstRow);
    
    requiredColumns.forEach(required => {
        if (!columns.includes(required)) {
            errors.push(`必要な列が見つかりません: ${required}`);
        }
    });

    // データ型の検証
    data.forEach((row, index) => {
        if (row['売上額'] && isNaN(parseFloat(row['売上額']))) {
            errors.push(`行 ${index + 2}: 売上額が数値ではありません`);
        }
        if (row['日付'] && !isValidDate(row['日付'])) {
            errors.push(`行 ${index + 2}: 日付形式が正しくありません`);
        }
    });

    return {
        isValid: errors.length === 0,
        errors
    };
}

/**
 * 日付の妥当性チェック
 */
function isValidDate(dateString) {
    const date = new Date(dateString);
    return !isNaN(date.getTime());
}

/**
 * Enhanced DeepResearch で売上データを分析
 */
async function analyzeSalesData(salesData) {
    try {
        // 基本統計計算
        const totalSales = salesData.reduce((sum, row) => {
            const amount = parseFloat(row['売上額']) || 0;
            return sum + amount;
        }, 0);

        const averageSales = totalSales / salesData.length;
        
        // 商品別売上
        const productSales = {};
        salesData.forEach(row => {
            const product = row['商品名'] || '不明';
            const amount = parseFloat(row['売上額']) || 0;
            productSales[product] = (productSales[product] || 0) + amount;
        });

        // 上位商品
        const topProducts = Object.entries(productSales)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5)
            .map(([product, sales]) => ({ product, sales }));

        // 期間分析
        const dates = salesData.map(row => new Date(row['日付'])).filter(d => !isNaN(d));
        const dateRange = dates.length > 0 ? {
            start: new Date(Math.min(...dates)),
            end: new Date(Math.max(...dates))
        } : null;

        return {
            summary: {
                total_sales: totalSales,
                average_sales: averageSales,
                record_count: salesData.length,
                date_range: dateRange
            },
            top_products: topProducts,
            insights: generateSalesInsights(salesData, totalSales, averageSales),
            analysis_time: new Date().toISOString()
        };

    } catch (error) {
        throw new Error(`売上分析エラー: ${error.message}`);
    }
}

/**
 * 売上インサイトの生成
 */
function generateSalesInsights(data, totalSales, averageSales) {
    const insights = [];
    
    if (totalSales > 1000000) {
        insights.push('📈 総売上が100万円を超えています（好調）');
    }
    
    if (averageSales > 10000) {
        insights.push('💰 平均売上が1万円を超えています（高単価）');
    }
    
    const uniqueProducts = new Set(data.map(row => row['商品名'])).size;
    if (uniqueProducts > 10) {
        insights.push('🛍️ 商品の多様性が高い（10商品以上）');
    }
    
    return insights;
}

/**
 * 売上データの保存（簡易版）
 */
async function saveSalesData(salesData, analysisResult) {
    // 実際の実装ではデータベースに保存
    const savedData = {
        id: `sales_${Date.now()}`,
        data: salesData,
        analysis: analysisResult,
        saved_at: new Date().toISOString()
    };
    
    // ここでファイルシステムまたはクラウドストレージに保存
    console.log('Saved sales data:', savedData.id);
    
    return savedData;
} 