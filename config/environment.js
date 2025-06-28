/**
 * 環境設定ファイル - 週次ビジネスレポートシステム
 * 本番環境とローカル環境の自動切り替え
 */

// 環境判定
const isProduction = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
const isAdminSite = window.location.hostname.includes('admin') || window.location.pathname.includes('admin');

// 環境別設定
export const config = {
  // 開発環境
  development: {
    apiUrl: 'http://127.0.0.1:5001/api',
    adminSiteUrl: 'http://localhost:8000',
    viewerSiteUrl: 'http://localhost:8003',
    debug: true,
    analytics: false
  },
  
  // 本番環境
  production: {
    apiUrl: 'https://admin-weeklyreport.netlify.app/.netlify/functions',
    adminSiteUrl: 'https://admin-weeklyreport.netlify.app',
    viewerSiteUrl: 'https://weeklyreport.netlify.app',
    debug: false,
    analytics: true
  }
};

// 現在の環境設定
export const currentConfig = isProduction ? config.production : config.development;

// サイト種別判定
export const siteType = isAdminSite ? 'admin' : 'viewer';

// API エンドポイント設定
export const apiEndpoints = {
  health: `${currentConfig.apiUrl}/health`,
  deepresearch: {
    analyze: `${currentConfig.apiUrl}/deepresearch-analyze`,
    status: `${currentConfig.apiUrl}/deepresearch-status`
  },
  news: {
    collect: `${currentConfig.apiUrl}/manage-news`,
    analyze: `${currentConfig.apiUrl}/manage-news`
  },
  reports: {
    generate: `${currentConfig.apiUrl}/generate-report`
  },
  sales: {
    upload: `${currentConfig.apiUrl}/upload-sales`
  }
};

// CORS設定
export const corsConfig = {
  credentials: 'same-origin',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};

// キャッシュ設定
export const cacheConfig = {
  // キャッシュ有効期限（ミリ秒）
  reportCache: 30 * 60 * 1000,      // 30分
  newsCache: 15 * 60 * 1000,        // 15分
  statsCache: 5 * 60 * 1000,        // 5分
  
  // LocalStorage キー
  keys: {
    reports: 'weeklyreport_reports',
    news: 'weeklyreport_news',
    stats: 'weeklyreport_stats',
    theme: 'weeklyreport_theme',
    settings: 'weeklyreport_settings'
  }
};

// ログ設定
export const logConfig = {
  level: currentConfig.debug ? 'debug' : 'error',
  enableConsole: currentConfig.debug,
  enableRemote: currentConfig.analytics
};

// 機能フラグ
export const features = {
  // 管理者サイト専用機能
  admin: {
    deepresearch: true,
    newsManagement: true,
    userManagement: false,  // 将来の機能
    advancedAnalytics: true
  },
  
  // 閲覧者サイト機能
  viewer: {
    darkMode: true,
    export: true,
    sharing: false,         // 将来の機能
    comments: false         // 将来の機能
  },
  
  // 共通機能
  common: {
    notifications: true,
    offline: false,         // PWA機能（将来）
    realtime: false         // リアルタイム更新（将来）
  }
};

// デバッグ用ヘルパー
export const debug = {
  log: (...args) => {
    if (currentConfig.debug) {
      console.log('[WeeklyReport]', ...args);
    }
  },
  
  error: (...args) => {
    console.error('[WeeklyReport Error]', ...args);
  },
  
  info: (...args) => {
    if (currentConfig.debug) {
      console.info('[WeeklyReport Info]', ...args);
    }
  }
};

// 初期化ログ
debug.log('Environment initialized:', {
  environment: isProduction ? 'production' : 'development',
  siteType: siteType,
  apiUrl: currentConfig.apiUrl,
  hostname: window.location.hostname
});

export default {
  config: currentConfig,
  siteType,
  apiEndpoints,
  corsConfig,
  cacheConfig,
  logConfig,
  features,
  debug
}; 