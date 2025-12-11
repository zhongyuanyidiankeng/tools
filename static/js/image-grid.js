/**
 * 图片网格切割组件
 * 支持可拖拽的行列切割线
 */
class ImageGridSplitter {
  constructor(containerId, options = {}) {
    this.container = document.getElementById(containerId);
    this.rows = options.rows || 2;
    this.cols = options.cols || 2;
    this.image = null;
    this.rowPositions = [];
    this.colPositions = [];
    this.onUpdate = options.onUpdate || (() => {});
    
    this.init();
  }
  
  init() {
    this.container.style.position = 'relative';
    this.container.style.userSelect = 'none';
  }
  
  setImage(imageSrc) {
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        this.image = img;
        this.render();
        resolve();
      };
      img.src = imageSrc;
    });
  }
  
  setGrid(rows, cols) {
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
    
    this.render();
  }
  
  render() {
    if (!this.image) return;
    
    this.container.innerHTML = '';
    
    // 创建画布
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // 计算显示尺寸
    const maxWidth = this.container.clientWidth || 600;
    const scale = Math.min(1, maxWidth / this.image.width);
    canvas.width = this.image.width * scale;
    canvas.height = this.image.height * scale;
    
    // 绘制图片
    ctx.drawImage(this.image, 0, 0, canvas.width, canvas.height);
    
    this.container.appendChild(canvas);
    
    // 绘制切割线
    this.drawLines(canvas);
  }
  
  drawLines(canvas) {
    const width = canvas.width;
    const height = canvas.height;
    
    // 行切割线
    this.rowPositions.forEach((pos, index) => {
      const line = this.createLine('horizontal', pos * height, width, index);
      this.container.appendChild(line);
    });
    
    // 列切割线
    this.colPositions.forEach((pos, index) => {
      const line = this.createLine('vertical', pos * width, height, index);
      this.container.appendChild(line);
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
      
      let newValue = Math.max(0.05, Math.min(0.95, startValue + delta));
      
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
