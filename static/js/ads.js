/**
 * 广告集成模块
 * 异步加载广告脚本，不阻塞页面渲染
 */

// 广告配置（部署时替换为真实的广告 ID）
const AD_CONFIG = {
  adsense: {
    clientId: 'ca-pub-XXXXXXXXXXXXXXXX',  // 替换为你的 AdSense 客户端 ID
    enabled: false  // 设置为 true 启用广告
  }
};

/**
 * 异步加载 Google AdSense
 */
function loadAdSense() {
  if (!AD_CONFIG.adsense.enabled) return;
  
  const script = document.createElement('script');
  script.src = `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${AD_CONFIG.adsense.clientId}`;
  script.async = true;
  script.crossOrigin = 'anonymous';
  document.head.appendChild(script);
}

/**
 * 创建广告位占位符
 */
function createAdSlot(containerId, format = 'auto') {
  if (!AD_CONFIG.adsense.enabled) return;
  
  const container = document.getElementById(containerId);
  if (!container) return;
  
  const ins = document.createElement('ins');
  ins.className = 'adsbygoogle';
  ins.style.display = 'block';
  ins.setAttribute('data-ad-client', AD_CONFIG.adsense.clientId);
  ins.setAttribute('data-ad-slot', 'XXXXXXXXXX');  // 替换为广告位 ID
  ins.setAttribute('data-ad-format', format);
  ins.setAttribute('data-full-width-responsive', 'true');
  
  container.appendChild(ins);
  
  // 推送广告
  (window.adsbygoogle = window.adsbygoogle || []).push({});
}

/**
 * 初始化广告
 * 在页面加载完成后调用
 */
function initAds() {
  // 延迟加载广告，优先保证工具功能
  if (document.readyState === 'complete') {
    setTimeout(loadAdSense, 1000);
  } else {
    window.addEventListener('load', () => {
      setTimeout(loadAdSense, 1000);
    });
  }
}

// 自动初始化
initAds();

// 导出
window.createAdSlot = createAdSlot;
