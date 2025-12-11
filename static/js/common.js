/**
 * 在线工具平台 - 公共 JavaScript
 */

// API 基础路径
const API_BASE = '/api/v1';

/**
 * 文件上传处理
 */
class FileUploader {
  constructor(uploadAreaId, options = {}) {
    this.uploadArea = document.getElementById(uploadAreaId);
    this.fileInput = this.uploadArea?.querySelector('input[type="file"]');
    this.onFileSelect = options.onFileSelect || (() => {});
    this.acceptTypes = options.acceptTypes || '*/*';
    
    if (this.uploadArea && this.fileInput) {
      this.init();
    }
  }
  
  init() {
    // 点击上传
    this.uploadArea.addEventListener('click', () => this.fileInput.click());
    
    // 文件选择
    this.fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.onFileSelect(e.target.files);
      }
    });
    
    // 拖拽上传
    this.uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      this.uploadArea.classList.add('dragover');
    });
    
    this.uploadArea.addEventListener('dragleave', () => {
      this.uploadArea.classList.remove('dragover');
    });
    
    this.uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      this.uploadArea.classList.remove('dragover');
      if (e.dataTransfer.files.length > 0) {
        this.onFileSelect(e.dataTransfer.files);
      }
    });
  }
}

/**
 * API 请求封装
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options.headers,
      }
    });
    
    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    return { success: false, error_message: error.message };
  }
}

/**
 * 上传文件到服务器
 */
async function uploadFile(file, endpoint) {
  const formData = new FormData();
  formData.append('file', file);
  
  return apiRequest(endpoint, {
    method: 'POST',
    body: formData
  });
}

/**
 * 显示结果
 */
function showResult(elementId, success, message) {
  const resultArea = document.getElementById(elementId);
  if (!resultArea) return;
  
  resultArea.className = `result-area show ${success ? 'success' : 'error'}`;
  resultArea.innerHTML = message;
}

/**
 * 显示/隐藏加载状态
 */
function setLoading(buttonId, loading) {
  const button = document.getElementById(buttonId);
  const loadingEl = document.getElementById(`${buttonId}-loading`);
  
  if (button) {
    button.disabled = loading;
  }
  if (loadingEl) {
    loadingEl.classList.toggle('show', loading);
  }
}

/**
 * 下载文件
 */
function downloadFile(url, filename) {
  const a = document.createElement('a');
  a.href = url;
  a.download = filename || 'download';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * 复制到剪贴板
 */
async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    // 降级方案
    const textarea = document.createElement('textarea');
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return true;
  }
}

/**
 * 格式化文件大小
 */
function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 导出到全局
window.FileUploader = FileUploader;
window.apiRequest = apiRequest;
window.uploadFile = uploadFile;
window.showResult = showResult;
window.setLoading = setLoading;
window.downloadFile = downloadFile;
window.copyToClipboard = copyToClipboard;
window.formatFileSize = formatFileSize;
