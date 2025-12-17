/**
 * 图片网格切割组件
 * 支持可拖拽的行列切割线
 */
class ImageGridSplitter {
  constructor(containerId, options = {}) {
    console.log('[ImageGridSplitter] 构造函数, containerId:', containerId);
    this.container = document.getElementById(containerId);
    console.log('[ImageGridSplitter] container 元素:', this.container);
    this.rows = options.rows || 2;
    this.cols = options.cols || 2;
    this.image = null;
    this.rowPositions = [];
    this.colPositions = [];
    this.onUpdate = options.onUpdate || (() => {});
    
    this.init();
  }
  
  init() {
    console.log('[ImageGridSplitter] init 调用');
    if (!this.container) {
      console.error('[ImageGridSplitter] container 不存在!');
      return;
    }
    this.container.style.position = 'relative';
    this.container.style.userSelect = 'none';
  }
  
  setImage(imageSrc) {
    console.log('[ImageGridSplitter] setImage 调用, src长度:', imageSrc ? imageSrc.length : 0);
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        console.log('[ImageGridSplitter] 图片加载成功, 尺寸:', img.width, 'x', img.height);
        this.image = img;
        this.render();
        resolve();
      };
      img.onerror = (err) => {
        console.error('[ImageGridSplitter] 图片加载失败:', err);
        reject(err);
      };
      img.src = imageSrc;
    });
  }
  
  setGrid(rows, cols) {
    console.log('[ImageGridSplitter] setGrid 调用:', rows, 'x', cols);
    this.rows = rows;
    this.cols = cols;
    this.rowPositions = [];
    this.colPositions = [];
    
    // 初始化均匀分布的位置
    for (let i = 1; i < rows; i++) {
      this.rowPositions.push(i / rows);
    }
    for (let i = 1; i < cols; i++) {
      this.colPositions.push(i / cols);
    }
    
    console.log('[ImageGridSplitter] rowPositions:', this.rowPositions);
    console.log('[ImageGridSplitter] colPositions:', this.colPositions);
    this.render();
  }
  
  render() {
    console.log('[ImageGridSplitter] render 调用, image:', this.image ? '存在' : '不存在');
    if (!this.image) {
      console.warn('[ImageGridSplitter] 没有图片，跳过渲染');
      return;
    }
    
    this.container.innerHTML = '';
    
    // 创建画布
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 计算显示尺寸
    const maxWidth = this.container.clientWidth || 600;
    console.log('[ImageGridSplitter] container宽度:', this.container.clientWidth, '使用maxWidth:', maxWidth);
    const scale = Math.min(1, maxWidth / this.image.width);
    canvas.width = this.image.width * scale;
    canvas.height = this.image.height * scale;
    console.log('[ImageGridSplitter] canvas尺寸:', canvas.width, 'x', canvas.height, 'scale:', scale);
    
    // 绘制图片
    ctx.drawImage(this.image, 0, 0, canvas.width, canvas.height);
    
    this.container.appendChild(canvas);
    console.log('[ImageGridSplitter] canvas 已添加到容器');
    
    // 绘制切割线
    this.drawLines(canvas);
  }
  
  drawLines(canvas) {
    const width = canvas.width;
    const height = canvas.height;
    console.log('[ImageGridSplitter] drawLines, canvas尺寸:', width, 'x', height);
    console.log('[ImageGridSplitter] 行线数量:', this.rowPositions.length, '列线数量:', this.colPositions.length);
    
    // 行切割线
    this.rowPositions.forEach((pos, index) => {
      const line = this.createLine('horizontal', pos * height, width, index);
      this.container.appendChild(line);
      console.log('[ImageGridSplitter] 添加行线', index, '位置:', pos * height);
    });
    
    // 列切割线
    this.colPositions.forEach((pos, index) => {
      const line = this.createLine('vertical', pos * width, height, index);
      this.container.appendChild(line);
      console.log('[ImageGridSplitter] 添加列线', index, '位置:', pos * width);
    });
    
    // 显示网格预览
    this.updatePreview();
  }
  
  createLine(type, position, length, index) {
    const line = document.createElement('div');
    line.className = `grid-line ${type}`;
    line.style.position = 'absolute';
    line.style.background = '#3b82f6';
    line.style.cursor = type === 'horizontal' ? 'row-resize' : 'col-resize';
    
    if (type === 'horizontal') {
      line.style.left = '0';
      line.style.top = `${position}px`;
      line.style.width = `${length}px`;
      line.style.height = '3px';
    } else {
      line.style.top = '0';
      line.style.left = `${position}px`;
      line.style.height = `${length}px`;
      line.style.width = '3px';
    }
    
    // 拖拽处理
    this.addDragHandler(line, type, index);
    
    return line;
  }
  
  addDragHandler(line, type, index) {
    let startPos = 0;
    let startValue = 0;
    
    const onMouseDown = (e) => {
      e.preventDefault();
      startPos = type === 'horizontal' ? e.clientY : e.clientX;
      startValue = type === 'horizontal' ? this.rowPositions[index] : this.colPositions[index];
      
      document.addEventListener('mousemove', onMouseMove);
      document.addEventListener('mouseup', onMouseUp);
    };
    
    const onMouseMove = (e) => {
      const canvas = this.container.querySelector('canvas');
      const rect = canvas.getBoundingClientRect();
      const size = type === 'horizontal' ? rect.height : rect.width;
      const currentPos = type === 'horizontal' ? e.clientY : e.clientX;
      const delta = (currentPos - startPos) / size;
      
      // 允许拖拽到边缘，但保留最小间距防止完全重叠
      let newValue = Math.max(0.01, Math.min(0.99, startValue + delta));
      
      if (type === 'horizontal') {
        this.rowPositions[index] = newValue;
      } else {
        this.colPositions[index] = newValue;
      }
      
      this.render();
    };
    
    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      this.onUpdate(this.getPositions());
    };
    
    line.addEventListener('mousedown', onMouseDown);
  }
  
  updatePreview() {
    // 显示切割后的区块数量
    const info = document.getElementById('grid-info');
    if (info) {
      info.textContent = `将切割为 ${this.rows} × ${this.cols} = ${this.rows * this.cols} 个区块`;
    }
  }
  
  getPositions() {
    return {
      rows: this.rows,
      cols: this.cols,
      rowPositions: [...this.rowPositions],
      colPositions: [...this.colPositions]
    };
  }
}

window.ImageGridSplitter = ImageGridSplitter;
