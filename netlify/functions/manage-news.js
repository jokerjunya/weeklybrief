/**
 * Netlify Function: ニュース管理システム
 * 
 * ニュース収集、分析、優先度設定、承認・却下機能
 */

exports.handler = async (event, context) => {
    const headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Content-Type': 'application/json'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        const { action, newsData, newsId, priority, status } = JSON.parse(event.body || '{}');
        
        let result;
        switch (action) {
            case 'collect':
                result = await collectNews(newsData);
                break;
            case 'analyze':
                result = await analyzeNews(newsData);
                break;
            case 'prioritize':
                result = await setPriority(newsId, priority);
                break;
            case 'approve':
                result = await approveNews(newsId);
                break;
            case 'reject':
                result = await rejectNews(newsId);
                break;
            case 'list':
                result = await listNews();
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
        console.error('News Management Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: 'ニュース管理エラー',
                message: error.message
            })
        };
    }
};

/**
 * ニュース収集
 */
async function collectNews(topics) {
    try {
        // AI業界の主要ニュースソースを模擬
        const mockNewsData = await fetchMockNewsData(topics || ['AI', 'artificial intelligence']);
        
        // Enhanced DeepResearch で各ニュースの関連性を分析
        const analyzedNews = await Promise.all(
            mockNewsData.map(async (news) => {
                const analysis = await performQuickAnalysis(news);
                return {
                    ...news,
                    relevance_score: analysis.relevance_score,
                    key_points: analysis.key_points,
                    sentiment: analysis.sentiment,
                    category: analysis.category
                };
            })
        );

        // 関連性スコアでソート
        analyzedNews.sort((a, b) => b.relevance_score - a.relevance_score);

        return {
            status: 'success',
            collected_count: analyzedNews.length,
            news_items: analyzedNews,
            collection_summary: {
                high_relevance: analyzedNews.filter(n => n.relevance_score > 0.8).length,
                medium_relevance: analyzedNews.filter(n => n.relevance_score > 0.5 && n.relevance_score <= 0.8).length,
                low_relevance: analyzedNews.filter(n => n.relevance_score <= 0.5).length
            }
        };

    } catch (error) {
        throw new Error(`ニュース収集エラー: ${error.message}`);
    }
}

/**
 * 模擬ニュースデータの取得
 */
async function fetchMockNewsData(topics) {
    // 実際の実装ではRSSフィード、ニュースAPIなどから取得
    const mockNews = [
        {
            id: 'news_001',
            title: 'OpenAI、GPT-5の開発を発表 - 推論能力が大幅向上',
            content: 'OpenAIは次世代言語モデルGPT-5の開発を正式に発表しました。GPT-4と比較して推論能力、長期記憶、マルチモーダル処理が大幅に改善される予定です...',
            source: 'TechCrunch',
            url: 'https://techcrunch.com/gpt5-announcement',
            published_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2時間前
            author: 'John Smith'
        },
        {
            id: 'news_002', 
            title: 'Google、Bard AIに新機能追加 - リアルタイム情報アクセス',
            content: 'Googleは対話型AI「Bard」にリアルタイム情報へのアクセス機能を追加しました。これにより最新のニュースや情報を取得できるようになります...',
            source: 'Reuters',
            url: 'https://reuters.com/bard-update',
            published_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4時間前
            author: 'Sarah Johnson'
        },
        {
            id: 'news_003',
            title: 'Meta、新しいAIチップ開発計画を発表',
            content: 'Metaは自社開発のAI専用チップの開発計画を発表。メタバース関連のAI処理に最適化されたアーキテクチャを採用予定...',
            source: 'The Verge',
            url: 'https://theverge.com/meta-ai-chip',
            published_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6時間前
            author: 'Alex Chen'
        },
        {
            id: 'news_004',
            title: 'AI規制法案、欧州議会で可決',
            content: '欧州議会でAI規制に関する包括的な法案が可決されました。高リスクAIシステムに対する厳格な規制が導入される見込みです...',
            source: 'BBC Tech',
            url: 'https://bbc.com/ai-regulation-eu',
            published_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8時間前
            author: 'Emily Davis'
        },
        {
            id: 'news_005',
            title: 'Microsoft、Azure AIサービスを大幅アップデート',
            content: 'MicrosoftはAzure AI サービスの大幅なアップデートを発表。新しい画像生成、音声合成、自然言語処理機能が追加されます...',
            source: 'Microsoft News',
            url: 'https://news.microsoft.com/azure-ai-update',
            published_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12時間前
            author: 'David Wilson'
        }
    ];

    return mockNews;
}

/**
 * ニュースの簡易分析
 */
async function performQuickAnalysis(news) {
    try {
        // キーワードベースの関連性スコア計算
        const relevanceKeywords = [
            'AI', 'artificial intelligence', '人工知能', 'machine learning', 
            'deep learning', 'neural network', 'GPT', 'LLM', 'ChatGPT',
            'OpenAI', 'Google', 'Microsoft', 'Meta', 'Amazon'
        ];
        
        const content = (news.title + ' ' + news.content).toLowerCase();
        const keywordCount = relevanceKeywords.filter(keyword => 
            content.includes(keyword.toLowerCase())
        ).length;
        
        const relevanceScore = Math.min(keywordCount / 5, 1.0);
        
        // センチメント分析（簡易版）
        const positiveWords = ['improve', 'enhance', 'breakthrough', 'innovation', 'success'];
        const negativeWords = ['risk', 'concern', 'problem', 'failure', 'limitation'];
        
        const positiveCount = positiveWords.filter(word => content.includes(word)).length;
        const negativeCount = negativeWords.filter(word => content.includes(word)).length;
        
        let sentiment = 'neutral';
        if (positiveCount > negativeCount) sentiment = 'positive';
        else if (negativeCount > positiveCount) sentiment = 'negative';
        
        // カテゴリ分類
        let category = 'general';
        if (content.includes('regulation') || content.includes('law')) category = 'regulation';
        else if (content.includes('product') || content.includes('release')) category = 'product';
        else if (content.includes('research') || content.includes('development')) category = 'research';
        else if (content.includes('business') || content.includes('market')) category = 'business';
        
        // キーポイント抽出（簡易版）
        const keyPoints = extractKeyPoints(news.content);
        
        return {
            relevance_score: relevanceScore,
            sentiment: sentiment,
            category: category,
            key_points: keyPoints,
            analysis_confidence: 0.7 + (relevanceScore * 0.2)
        };
        
    } catch (error) {
        return {
            relevance_score: 0.5,
            sentiment: 'neutral',
            category: 'general',
            key_points: [],
            analysis_confidence: 0.3
        };
    }
}

/**
 * キーポイント抽出
 */
function extractKeyPoints(content) {
    const sentences = content.split('。').slice(0, 3); // 最初の3文
    return sentences.map(sentence => sentence.trim()).filter(sentence => sentence.length > 10);
}

/**
 * ニュース詳細分析
 */
async function analyzeNews(newsItems) {
    try {
        const detailedAnalysis = await Promise.all(
            newsItems.map(async (item) => {
                // Enhanced DeepResearch による詳細分析（模擬）
                const deepAnalysis = await performDeepAnalysis(item);
                
                return {
                    news_id: item.id,
                    deep_insights: deepAnalysis.insights,
                    impact_score: deepAnalysis.impact_score,
                    recommended_priority: deepAnalysis.recommended_priority,
                    confidence: deepAnalysis.confidence,
                    reasoning: deepAnalysis.reasoning
                };
            })
        );

        return {
            status: 'analyzed',
            analysis_results: detailedAnalysis
        };

    } catch (error) {
        throw new Error(`ニュース分析エラー: ${error.message}`);
    }
}

/**
 * 詳細分析実行
 */
async function performDeepAnalysis(newsItem) {
    // Enhanced DeepResearch による分析のシミュレーション
    const impactFactors = {
        source_credibility: getSourceCredibility(newsItem.source),
        content_depth: Math.min(newsItem.content.length / 1000, 1.0),
        recency: calculateRecencyScore(newsItem.published_at),
        keyword_density: calculateKeywordDensity(newsItem.content)
    };
    
    const impactScore = Object.values(impactFactors).reduce((sum, factor) => sum + factor, 0) / 4;
    
    let recommendedPriority = 'low';
    if (impactScore > 0.8) recommendedPriority = 'high';
    else if (impactScore > 0.5) recommendedPriority = 'medium';
    
    return {
        insights: [
            `情報源の信頼度: ${(impactFactors.source_credibility * 100).toFixed(0)}%`,
            `コンテンツの詳細度: ${(impactFactors.content_depth * 100).toFixed(0)}%`,
            `情報の新しさ: ${(impactFactors.recency * 100).toFixed(0)}%`
        ],
        impact_score: impactScore,
        recommended_priority: recommendedPriority,
        confidence: 0.8 + (impactScore * 0.15),
        reasoning: `総合的な影響スコアが${(impactScore * 100).toFixed(0)}%のため、${recommendedPriority}優先度を推奨します。`
    };
}

/**
 * 情報源の信頼度計算
 */
function getSourceCredibility(source) {
    const credibilityMap = {
        'TechCrunch': 0.9,
        'Reuters': 0.95,
        'The Verge': 0.85,
        'BBC Tech': 0.9,
        'Microsoft News': 0.8,
        'Google Blog': 0.8,
        'OpenAI Blog': 0.85
    };
    return credibilityMap[source] || 0.6;
}

/**
 * 新しさスコア計算
 */
function calculateRecencyScore(publishedAt) {
    const hoursAgo = (Date.now() - new Date(publishedAt).getTime()) / (1000 * 60 * 60);
    if (hoursAgo <= 2) return 1.0;
    if (hoursAgo <= 6) return 0.8;
    if (hoursAgo <= 24) return 0.6;
    return 0.3;
}

/**
 * キーワード密度計算
 */
function calculateKeywordDensity(content) {
    const importantKeywords = ['AI', 'breakthrough', 'innovation', 'development', 'new', 'advanced'];
    const words = content.toLowerCase().split(/\s+/);
    const keywordCount = words.filter(word => 
        importantKeywords.some(keyword => word.includes(keyword.toLowerCase()))
    ).length;
    return Math.min(keywordCount / words.length * 10, 1.0);
}

/**
 * 優先度設定
 */
async function setPriority(newsId, priority) {
    // 実際の実装ではデータベースを更新
    return {
        status: 'updated',
        news_id: newsId,
        new_priority: priority,
        updated_at: new Date().toISOString()
    };
}

/**
 * ニュース承認
 */
async function approveNews(newsId) {
    return {
        status: 'approved',
        news_id: newsId,
        approved_at: new Date().toISOString()
    };
}

/**
 * ニュース却下
 */
async function rejectNews(newsId) {
    return {
        status: 'rejected',
        news_id: newsId,
        rejected_at: new Date().toISOString()
    };
}

/**
 * ニュース一覧取得
 */
async function listNews() {
    // 模擬データベースからニュース一覧を取得
    return {
        status: 'success',
        total_count: 5,
        news_items: await fetchMockNewsData(['AI'])
    };
} 