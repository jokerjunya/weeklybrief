/**
 * Netlify Function: Enhanced DeepResearch API Proxy
 * 
 * 管理者サイトからのAPIリクエストをローカルのEnhanced DeepResearchサーバーに転送
 */

const https = require('https');
const http = require('http');

// Enhanced DeepResearch API サーバーの設定
const DEEPRESEARCH_API_HOST = process.env.DEEPRESEARCH_API_HOST || 'localhost';
const DEEPRESEARCH_API_PORT = process.env.DEEPRESEARCH_API_PORT || '5000';

exports.handler = async (event, context) => {
    // CORS ヘッダー
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Content-Type': 'application/json'
    };

    // OPTIONS リクエスト（プリフライト）への対応
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers,
            body: ''
        };
    }

    try {
        // APIパスの抽出（/api/ 以降）
        const apiPath = event.path.replace('/.netlify/functions/deepresearch-api', '') || '/api/health';
        
        // リクエストボディの処理
        let requestBody = '';
        if (event.body) {
            requestBody = event.isBase64Encoded ? 
                Buffer.from(event.body, 'base64').toString('utf-8') : 
                event.body;
        }

        // Enhanced DeepResearch API サーバーへのリクエスト
        const apiResponse = await makeApiRequest({
            method: event.httpMethod,
            path: apiPath,
            body: requestBody,
            headers: event.headers
        });

        return {
            statusCode: apiResponse.statusCode,
            headers,
            body: apiResponse.body
        };

    } catch (error) {
        console.error('DeepResearch API Proxy Error:', error);
        
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: 'Enhanced DeepResearch API 接続エラー',
                message: error.message,
                timestamp: new Date().toISOString()
            })
        };
    }
};

/**
 * Enhanced DeepResearch API サーバーへHTTPリクエストを送信
 */
function makeApiRequest({ method, path, body, headers }) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: DEEPRESEARCH_API_HOST,
            port: DEEPRESEARCH_API_PORT,
            path: path,
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Netlify-Functions-Proxy/1.0'
            }
        };

        // リクエストボディがある場合はContent-Lengthを設定
        if (body) {
            options.headers['Content-Length'] = Buffer.byteLength(body);
        }

        const req = http.request(options, (res) => {
            let responseBody = '';

            res.on('data', (chunk) => {
                responseBody += chunk;
            });

            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    body: responseBody
                });
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        // リクエストボディを送信
        if (body) {
            req.write(body);
        }
        
        req.end();
    });
} 