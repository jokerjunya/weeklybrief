/**
 * Netlify Function: 週次レポート生成システム
 * 
 * 売上データ、ニュース分析、イベント情報を統合して週次レポートを生成
 */

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        const { action, reportData, publishTarget } = JSON.parse(event.body || '{}');
        
        let result;
        switch (action) {
            case 'generate':
                result = await generateWeeklyReport(reportData);
                break;
            case 'preview':
                result = await previewReport(reportData);
                break;
            case 'publish':
                result = await publishReport(reportData, publishTarget);
                break;
            case 'status':
                result = await getReportStatus();
                break;
            default:
                throw new Error(`Unknown action: ${action}`);
        }

        return {
            statusCode: 200,
            headers,
            body: JSON.stringify(result)
        };

    } catch (error) {
        console.error('Report Generation Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: 'レポート生成エラー',
                message: error.message
            })
        };
    }
};

/**
 * 週次レポート生成
 */
async function generateWeeklyReport(reportData) {
    try {
        const {
            salesData,
            newsData,
            eventsData,
            reportConfig = {}
        } = reportData;

        // 1. 売上データ分析
        const salesAnalysis = await analyzeSalesData(salesData);
        
        // 2. ニュース要約生成
        const newsSummary = await generateNewsSummary(newsData);
        
        // 3. イベント情報整理
        const eventsFormatted = await formatEvents(eventsData);
        
        // 4. Enhanced DeepResearch による統合分析
        const integratedInsights = await generateIntegratedInsights(
            salesAnalysis, newsSummary, eventsFormatted
        );

        // 5. レポート構成生成
        const reportStructure = buildReportStructure({
            salesAnalysis,
            newsSummary,
            eventsFormatted,
            integratedInsights,
            config: reportConfig
        });

        // 6. HTML/Markdown生成
        const reportHTML = generateReportHTML(reportStructure);
        const reportMarkdown = generateReportMarkdown(reportStructure);

        return {
            status: 'generated',
            report_id: `report_${Date.now()}`,
            generation_time: new Date().toISOString(),
            structure: reportStructure,
            html: reportHTML,
            markdown: reportMarkdown,
            metadata: {
                total_sales: salesAnalysis.totalSales,
                news_count: newsSummary.count,
                events_count: eventsFormatted.length,
                insights_count: integratedInsights.length
            }
        };

    } catch (error) {
        throw new Error(`レポート生成エラー: ${error.message}`);
    }
}

/**
 * 売上データ分析
 */
async function analyzeSalesData(salesData) {
    if (!salesData || !Array.isArray(salesData)) {
        return {
            totalSales: 0,
            trend: 'no-data',
            topProducts: [],
            insights: ['売上データがありません']
        };
    }

    const totalSales = salesData.reduce((sum, item) => {
        return sum + (parseFloat(item['売上額']) || 0);
    }, 0);

    // 商品別売上集計
    const productSales = {};
    salesData.forEach(item => {
        const product = item['商品名'] || '不明';
        const amount = parseFloat(item['売上額']) || 0;
        productSales[product] = (productSales[product] || 0) + amount;
    });

    const topProducts = Object.entries(productSales)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([product, sales]) => ({ product, sales }));

    // トレンド分析（簡易版）
    const trend = totalSales > 100000 ? 'positive' : totalSales > 50000 ? 'neutral' : 'negative';

    const insights = [
        `📊 総売上: ¥${totalSales.toLocaleString()}`,
        `🏆 トップ商品: ${topProducts[0]?.product || '不明'} (¥${topProducts[0]?.sales?.toLocaleString() || 0})`,
        `📈 売上トレンド: ${trend === 'positive' ? '好調' : trend === 'neutral' ? '安定' : '改善が必要'}`
    ];

    return {
        totalSales,
        trend,
        topProducts,
        insights,
        averageSales: totalSales / salesData.length,
        transactionCount: salesData.length
    };
}

/**
 * ニュース要約生成
 */
async function generateNewsSummary(newsData) {
    if (!newsData || !Array.isArray(newsData)) {
        return {
            count: 0,
            summary: 'ニュースデータがありません',
            highlights: [],
            categories: {}
        };
    }

    // 承認されたニュースのみを対象
    const approvedNews = newsData.filter(news => 
        news.review_status === 'approved' || news.priority === 'high'
    );

    // カテゴリ別分類
    const categories = {};
    approvedNews.forEach(news => {
        const category = news.category || 'general';
        if (!categories[category]) categories[category] = [];
        categories[category].push(news);
    });

    // ハイライト生成
    const highlights = approvedNews
        .filter(news => news.relevance_score > 0.7)
        .slice(0, 3)
        .map(news => ({
            title: news.title,
            source: news.source,
            summary: news.content.substring(0, 100) + '...',
            impact_score: news.relevance_score
        }));

    const summary = generateTextSummary(approvedNews);

    return {
        count: approvedNews.length,
        summary,
        highlights,
        categories: Object.keys(categories).reduce((result, category) => {
            result[category] = categories[category].length;
            return result;
        }, {})
    };
}

/**
 * テキスト要約生成
 */
function generateTextSummary(newsItems) {
    if (newsItems.length === 0) return 'ニュースがありません';
    
    const majorTopics = [];
    if (newsItems.some(n => n.content.toLowerCase().includes('openai'))) {
        majorTopics.push('OpenAI');
    }
    if (newsItems.some(n => n.content.toLowerCase().includes('google'))) {
        majorTopics.push('Google');
    }
    if (newsItems.some(n => n.content.toLowerCase().includes('microsoft'))) {
        majorTopics.push('Microsoft');
    }

    let summary = `今週は${newsItems.length}件のAI関連ニュースを確認しました。`;
    
    if (majorTopics.length > 0) {
        summary += ` 主要な話題として${majorTopics.join('、')}関連の動向が注目されています。`;
    }

    const highImpactNews = newsItems.filter(n => n.relevance_score > 0.8);
    if (highImpactNews.length > 0) {
        summary += ` 特に影響度の高いニュースが${highImpactNews.length}件ありました。`;
    }

    return summary;
}

/**
 * イベント情報整理
 */
async function formatEvents(eventsData) {
    if (!eventsData || !Array.isArray(eventsData)) {
        return [];
    }

    return eventsData.map(event => ({
        date: event.date,
        title: event.title,
        description: event.description || '',
        category: event.category || 'general',
        importance: event.importance || 'medium'
    })).sort((a, b) => new Date(a.date) - new Date(b.date));
}

/**
 * 統合インサイト生成
 */
async function generateIntegratedInsights(salesAnalysis, newsSummary, eventsFormatted) {
    const insights = [];

    // 売上とニュースの相関分析
    if (salesAnalysis.trend === 'positive' && newsSummary.count > 0) {
        insights.push({
            type: 'correlation',
            title: '売上とAI動向の好循環',
            content: `売上が好調で、同時にAI業界のニュースも${newsSummary.count}件と活発です。技術動向への敏感さが売上に貢献している可能性があります。`,
            confidence: 0.7
        });
    }

    // イベントと売上の関連
    const upcomingEvents = eventsFormatted.filter(event => 
        new Date(event.date) > new Date()
    );
    
    if (upcomingEvents.length > 0) {
        insights.push({
            type: 'forecast',
            title: '今後のイベント予定',
            content: `${upcomingEvents.length}件のイベントが予定されており、売上への影響が期待されます。`,
            confidence: 0.6
        });
    }

    // ニュースカテゴリと売上の関連
    const techNews = newsSummary.categories?.research || 0;
    if (techNews > 0 && salesAnalysis.trend === 'positive') {
        insights.push({
            type: 'trend',
            title: '技術革新と業績の相関',
            content: `研究開発関連のニュースが${techNews}件あり、これが市場の関心を高めて売上向上に寄与している可能性があります。`,
            confidence: 0.8
        });
    }

    return insights;
}

/**
 * レポート構造構築
 */
function buildReportStructure(data) {
    const { salesAnalysis, newsSummary, eventsFormatted, integratedInsights, config } = data;
    
    return {
        header: {
            title: '週次ビジネスレポート',
            period: getWeekPeriod(),
            generated_at: new Date().toISOString(),
            version: '2.0 (Enhanced DeepResearch)'
        },
        executive_summary: {
            key_metrics: [
                `総売上: ¥${salesAnalysis.totalSales?.toLocaleString() || 0}`,
                `トレンド: ${salesAnalysis.trend}`,
                `ニュース件数: ${newsSummary.count}`,
                `今後のイベント: ${eventsFormatted.length}件`
            ],
            highlights: integratedInsights.slice(0, 2)
        },
        sections: [
            {
                id: 'sales',
                title: '📊 売上分析',
                content: salesAnalysis
            },
            {
                id: 'news',
                title: '📰 AI業界動向',
                content: newsSummary
            },
            {
                id: 'events',
                title: '📅 今週のイベント',
                content: eventsFormatted
            },
            {
                id: 'insights',
                title: '🔍 統合分析・インサイト',
                content: integratedInsights
            }
        ],
        footer: {
            generated_by: 'Enhanced DeepResearch System',
            data_sources: ['売上CSV', 'AI ニュース収集', 'イベントカレンダー'],
            confidence_score: calculateOverallConfidence(integratedInsights)
        }
    };
}

/**
 * 週間期間の取得
 */
function getWeekPeriod() {
    const today = new Date();
    const monday = new Date(today);
    monday.setDate(today.getDate() - today.getDay() + 1);
    
    const sunday = new Date(monday);
    sunday.setDate(monday.getDate() + 6);
    
    return {
        start: monday.toISOString().split('T')[0],
        end: sunday.toISOString().split('T')[0],
        week_number: getWeekNumber(today)
    };
}

/**
 * 週番号取得
 */
function getWeekNumber(date) {
    const firstDayOfYear = new Date(date.getFullYear(), 0, 1);
    const pastDaysOfYear = (date - firstDayOfYear) / 86400000;
    return Math.ceil((pastDaysOfYear + firstDayOfYear.getDay() + 1) / 7);
}

/**
 * 全体信頼度計算
 */
function calculateOverallConfidence(insights) {
    if (insights.length === 0) return 0.5;
    const totalConfidence = insights.reduce((sum, insight) => sum + insight.confidence, 0);
    return totalConfidence / insights.length;
}

/**
 * HTML レポート生成
 */
function generateReportHTML(structure) {
    const { header, executive_summary, sections, footer } = structure;
    
    return `
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${header.title} - ${header.period.start} ～ ${header.period.end}</title>
    <style>
        body { font-family: 'Hiragino Sans', sans-serif; line-height: 1.6; margin: 40px; }
        .header { text-align: center; border-bottom: 3px solid #2c3e50; padding-bottom: 20px; }
        .section { margin: 30px 0; }
        .metric { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 8px; }
        .highlight { background: #e8f5e8; padding: 10px; border-left: 4px solid #27ae60; }
    </style>
</head>
<body>
    <div class="header">
        <h1>${header.title}</h1>
        <p>期間: ${header.period.start} ～ ${header.period.end}</p>
        <p>生成日時: ${new Date(header.generated_at).toLocaleString()}</p>
    </div>
    
    <div class="section">
        <h2>📋 エグゼクティブサマリー</h2>
        ${executive_summary.key_metrics.map(metric => `<div class="metric">${metric}</div>`).join('')}
    </div>
    
    ${sections.map(section => `
        <div class="section">
            <h2>${section.title}</h2>
            ${generateSectionHTML(section)}
        </div>
    `).join('')}
    
    <div class="footer">
        <p><strong>Generated by:</strong> ${footer.generated_by}</p>
        <p><strong>Confidence Score:</strong> ${(footer.confidence_score * 100).toFixed(1)}%</p>
    </div>
</body>
</html>`;
}

/**
 * セクションHTML生成
 */
function generateSectionHTML(section) {
    switch (section.id) {
        case 'sales':
            return `
                <p>総売上: ¥${section.content.totalSales?.toLocaleString()}</p>
                <p>取引件数: ${section.content.transactionCount}件</p>
                <h4>トップ商品:</h4>
                <ul>
                    ${section.content.topProducts?.map(p => `<li>${p.product}: ¥${p.sales.toLocaleString()}</li>`).join('') || ''}
                </ul>
            `;
        case 'news':
            return `
                <p>${section.content.summary}</p>
                <h4>ハイライト:</h4>
                ${section.content.highlights?.map(h => `<div class="highlight">${h.title} (${h.source})</div>`).join('') || ''}
            `;
        case 'events':
            return section.content?.map(event => `
                <div class="metric">
                    <strong>${event.date}</strong>: ${event.title}<br>
                    ${event.description}
                </div>
            `).join('') || 'イベントなし';
        case 'insights':
            return section.content?.map(insight => `
                <div class="highlight">
                    <h4>${insight.title}</h4>
                    <p>${insight.content}</p>
                    <small>信頼度: ${(insight.confidence * 100).toFixed(0)}%</small>
                </div>
            `).join('') || '';
        default:
            return '<p>データなし</p>';
    }
}

/**
 * Markdown レポート生成
 */
function generateReportMarkdown(structure) {
    const { header, executive_summary, sections } = structure;
    
    return `# ${header.title}

**期間**: ${header.period.start} ～ ${header.period.end}  
**生成日時**: ${new Date(header.generated_at).toLocaleString()}

## 📋 エグゼクティブサマリー

${executive_summary.key_metrics.map(metric => `- ${metric}`).join('\n')}

${sections.map(section => `
## ${section.title}

${generateSectionMarkdown(section)}
`).join('')}

---
*Generated by Enhanced DeepResearch System*
`;
}

/**
 * セクションMarkdown生成
 */
function generateSectionMarkdown(section) {
    switch (section.id) {
        case 'sales':
            return `
- **総売上**: ¥${section.content.totalSales?.toLocaleString()}
- **取引件数**: ${section.content.transactionCount}件

### トップ商品
${section.content.topProducts?.map(p => `- ${p.product}: ¥${p.sales.toLocaleString()}`).join('\n') || ''}
`;
        case 'news':
            return `
${section.content.summary}

### ハイライト
${section.content.highlights?.map(h => `- **${h.title}** (${h.source})`).join('\n') || ''}
`;
        case 'events':
            return section.content?.map(event => `
- **${event.date}**: ${event.title}
  ${event.description}
`).join('') || 'イベントなし';
        case 'insights':
            return section.content?.map(insight => `
### ${insight.title}
${insight.content}
*信頼度: ${(insight.confidence * 100).toFixed(0)}%*
`).join('') || '';
        default:
            return 'データなし';
    }
}

/**
 * レポートプレビュー
 */
async function previewReport(reportData) {
    const generated = await generateWeeklyReport(reportData);
    
    return {
        status: 'preview',
        preview_html: generated.html.substring(0, 2000) + '...',
        structure: generated.structure,
        metadata: generated.metadata
    };
}

/**
 * レポート公開
 */
async function publishReport(reportData, target = 'viewer-site') {
    try {
        const report = await generateWeeklyReport(reportData);
        
        // 実際の実装では閲覧者サイトのdata/ディレクトリに保存
        const publishResult = {
            status: 'published',
            published_at: new Date().toISOString(),
            target: target,
            url: `https://weeklyreport.netlify.app/report-${report.report_id}`,
            report_id: report.report_id
        };

        return publishResult;

    } catch (error) {
        throw new Error(`レポート公開エラー: ${error.message}`);
    }
}

/**
 * レポート状況取得
 */
async function getReportStatus() {
    return {
        last_generated: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        next_scheduled: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
        total_reports: 12,
        system_status: 'operational'
    };
} 