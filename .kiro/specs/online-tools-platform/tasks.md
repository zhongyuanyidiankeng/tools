# Implementation Plan

- [x] 1. 项目初始化和核心基础设施


  - [x] 1.1 创建项目结构和依赖配置


    - 创建目录结构：api/, core/, services/, static/, tests/
    - 创建 requirements.txt 包含所有 Python 依赖
    - 创建 FastAPI 应用入口 main.py


    - _Requirements: 6.1, 6.2_
  - [ ] 1.2 实现文件处理器核心模块
    - 创建 core/file_handler.py
    - 实现文件类型验证（基于 magic bytes）


    - 实现临时文件保存和获取


    - 实现过期文件清理逻辑
    - _Requirements: 5.1, 5.2_
  - [x] 1.3 编写属性测试：文件类型检测准确性


    - **Property 19: 文件类型检测准确性**


    - **Validates: Requirements 5.1**

  - [x] 1.4 实现任务队列模块


    - 创建 core/task_queue.py
    - 实现基于 asyncio.Semaphore 的并发控制
    - 限制最大并发处理数为 3
    - _Requirements: 6.3_
  - [x] 1.5 创建通用数据模型


    - 创建 models/schemas.py

    - 定义 FileUploadResponse, ProcessingResult, ValidationResult 等
    - _Requirements: 5.1, 5.4_


- [x] 2. Checkpoint - 确保所有测试通过

  - Ensure all tests pass, ask the user if questions arise.



- [ ] 3. 文本工具服务实现
  - [ ] 3.1 实现文本服务核心模块
    - 创建 services/text_service.py
    - 实现 JSON 格式化（带错误位置检测）
    - 实现 Base64 编解码

    - 实现正则表达式测试


    - 实现 Markdown 转 HTML
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  - [ ] 3.2 编写属性测试：JSON 格式化往返一致性
    - **Property 12: JSON 格式化往返一致性**
    - **Validates: Requirements 3.1**


  - [x] 3.3 编写属性测试：Base64 编解码往返一致性

    - **Property 13: Base64 编解码往返一致性**
    - **Validates: Requirements 3.2, 3.3**

  - [ ] 3.4 编写属性测试：正则匹配正确性
    - **Property 14: 正则匹配正确性**


    - **Validates: Requirements 3.4**
  - [ ] 3.5 编写属性测试：Markdown 转换有效性
    - **Property 15: Markdown 转换有效性**
    - **Validates: Requirements 3.5**
  - [x] 3.6 创建文本工具 API 路由




    - 创建 api/text.py


    - 实现 /api/v1/text/json-format 端点
    - 实现 /api/v1/text/base64 端点
    - 实现 /api/v1/text/regex-test 端点
    - 实现 /api/v1/text/markdown 端点
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_




- [ ] 4. 开发者工具服务实现
  - [x] 4.1 实现开发者工具服务核心模块

    - 创建 services/dev_service.py
    - 实现 JWT 解码（header, payload, 签名状态）

    - 实现 Cron 表达式生成和下次执行时间计算
    - 实现 UUID v4 生成
    - 实现 IP 地理位置查询

    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [x] 4.2 编写属性测试：JWT 解码正确性

    - **Property 16: JWT 解码正确性**
    - **Validates: Requirements 4.1**

  - [ ] 4.3 编写属性测试：Cron 表达式有效性
    - **Property 17: Cron 表达式有效性**
    - **Validates: Requirements 4.2**

  - [ ] 4.4 编写属性测试：UUID 格式有效性
    - **Property 18: UUID 格式有效性**


    - **Validates: Requirements 4.3**
  - [ ] 4.5 创建开发者工具 API 路由
    - 创建 api/dev.py
    - 实现 /api/v1/dev/jwt-decode 端点
    - 实现 /api/v1/dev/cron-generate 端点
    - 实现 /api/v1/dev/uuid 端点
    - 实现 /api/v1/dev/ip-lookup 端点
    - _Requirements: 4.1, 4.2, 4.3, 4.4_




- [x] 5. Checkpoint - 确保所有测试通过


  - Ensure all tests pass, ask the user if questions arise.

- [ ] 6. 图像处理服务实现
  - [ ] 6.1 实现图像服务核心模块
    - 创建 services/image_service.py
    - 实现基础图片压缩


    - 实现指定大小压缩（二分法调整质量）

    - 实现格式转换（WebP -> JPG 等）
    - 实现图片裁剪

    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 6.2 编写属性测试：指定大小压缩

    - **Property 6: 指定大小压缩**
    - **Validates: Requirements 2.2**

  - [ ] 6.3 编写属性测试：格式转换有效性
    - **Property 7: 格式转换有效性**


    - **Validates: Requirements 2.3**
  - [ ] 6.4 编写属性测试：裁剪尺寸正确性
    - **Property 8: 裁剪尺寸正确性**
    - **Validates: Requirements 2.4**
  - [ ] 6.5 实现网格切割功能
    - 实现 grid_split 方法（按行列位置切割）




    - 实现 split_and_compress 方法（切割并压缩）


    - _Requirements: 2.5, 2.6, 2.7, 2.8_
  - [ ] 6.6 编写属性测试：网格切割数量正确性
    - **Property 9: 网格切割数量正确性**


    - **Validates: Requirements 2.7**
  - [ ] 6.7 编写属性测试：切割并压缩组合正确性
    - **Property 10: 切割并压缩组合正确性**


    - **Validates: Requirements 2.8**
  - [ ] 6.8 实现 ICO 生成功能
    - 实现 to_ico 方法

    - 支持标准图标尺寸 (16, 32, 48, 256)
    - _Requirements: 2.9_
  - [ ] 6.9 编写属性测试：ICO 生成有效性
    - **Property 11: ICO 生成有效性**
    - **Validates: Requirements 2.9**
  - [x] 6.10 创建图像工具 API 路由

    - 创建 api/image.py
    - 实现 /api/v1/image/compress 端点
    - 实现 /api/v1/image/compress-to-size 端点
    - 实现 /api/v1/image/convert 端点
    - 实现 /api/v1/image/crop 端点
    - 实现 /api/v1/image/grid-split 端点
    - 实现 /api/v1/image/split-compress 端点
    - 实现 /api/v1/image/to-ico 端点

    - _Requirements: 2.1-2.10_

- [ ] 7. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 8. PDF 处理服务实现
  - [ ] 8.1 实现 PDF 服务核心模块
    - 创建 services/pdf_service.py
    - 实现 PDF 压缩（目标 30%+ 压缩率）
    - 实现 PDF 转 Word


    - 实现 PDF 合并

    - 实现 PDF 拆分
    - 实现图片转 PDF

    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_


  - [ ] 8.2 编写属性测试：PDF 压缩有效性
    - **Property 1: PDF 压缩有效性**

    - **Validates: Requirements 1.1**

  - [ ] 8.3 编写属性测试：PDF 转 Word 有效性
    - **Property 2: PDF 转 Word 有效性**

    - **Validates: Requirements 1.2**


  - [ ] 8.4 编写属性测试：PDF 合并完整性
    - **Property 3: PDF 合并完整性**
    - **Validates: Requirements 1.3**

  - [ ] 8.5 编写属性测试：PDF 拆分正确性
    - **Property 4: PDF 拆分正确性**


    - **Validates: Requirements 1.4**
  - [x] 8.6 编写属性测试：图片转 PDF 完整性



    - **Property 5: 图片转 PDF 完整性**
    - **Validates: Requirements 1.5**
  - [ ] 8.7 创建 PDF 工具 API 路由
    - 创建 api/pdf.py
    - 实现 /api/v1/pdf/compress 端点
    - 实现 /api/v1/pdf/to-word 端点
    - 实现 /api/v1/pdf/merge 端点
    - 实现 /api/v1/pdf/split 端点
    - 实现 /api/v1/pdf/from-images 端点
    - _Requirements: 1.1-1.6_

- [ ] 9. Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 10. 前端页面实现
  - [ ] 10.1 创建前端基础结构和公共组件
    - 创建 static/css/style.css（Tailwind 配置）
    - 创建 static/js/common.js（文件上传、下载、错误处理）
    - 创建基础 HTML 模板结构
    - _Requirements: 7.1, 7.2_
  - [ ] 10.2 实现图片切割拖拽交互组件
    - 创建 static/js/image-grid.js
    - 实现可拖拽的行列切割线
    - 实现实时预览切割效果
    - _Requirements: 2.5, 2.6_
  - [ ] 10.3 创建首页和工具导航
    - 创建 static/index.html
    - 实现工具分类导航
    - 添加 SEO 元标签
    - _Requirements: 7.1, 7.2_
  - [ ] 10.4 创建 PDF 工具页面
    - 创建 static/tools/pdf/compress.html
    - 创建 static/tools/pdf/to-word.html
    - 创建 static/tools/pdf/merge.html
    - 创建 static/tools/pdf/split.html
    - 创建 static/tools/pdf/from-images.html
    - _Requirements: 1.1-1.6, 7.1, 7.2_
  - [ ] 10.5 创建图像工具页面
    - 创建 static/tools/image/compress.html
    - 创建 static/tools/image/compress-to-size.html
    - 创建 static/tools/image/convert.html
    - 创建 static/tools/image/crop.html
    - 创建 static/tools/image/grid-split.html
    - 创建 static/tools/image/split-compress.html
    - 创建 static/tools/image/to-ico.html
    - _Requirements: 2.1-2.10, 7.1, 7.2_
  - [ ] 10.6 创建文本工具页面
    - 创建 static/tools/text/json-format.html
    - 创建 static/tools/text/base64.html
    - 创建 static/tools/text/regex-test.html
    - 创建 static/tools/text/markdown.html
    - _Requirements: 3.1-3.6, 7.1, 7.2_
  - [ ] 10.7 创建开发者工具页面
    - 创建 static/tools/dev/jwt-decode.html
    - 创建 static/tools/dev/cron-generate.html
    - 创建 static/tools/dev/uuid.html
    - 创建 static/tools/dev/ip-lookup.html
    - _Requirements: 4.1-4.4, 7.1, 7.2_
  - [ ] 10.8 编写属性测试：页面元数据完整性
    - **Property 20: 页面元数据完整性**
    - **Validates: Requirements 7.1**
  - [ ] 10.9 编写属性测试：HTML 语义结构正确性
    - **Property 21: HTML 语义结构正确性**
    - **Validates: Requirements 7.2**

- [ ] 11. SEO 和广告集成
  - [ ] 11.1 实现 Sitemap 生成
    - 创建 static/sitemap.xml 或动态生成端点
    - 包含所有工具页面 URL
    - _Requirements: 7.3_
  - [ ] 11.2 集成广告代码
    - 在工具页面添加广告位占位符
    - 实现异步加载广告脚本
    - 确保移动端适配
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 12. 安全和性能优化
  - [ ] 12.1 实现请求限流
    - 添加速率限制中间件
    - 返回 429 状态和 retry-after 信息
    - _Requirements: 5.4_
  - [ ] 12.2 实现 CSRF 保护
    - 添加 CSRF token 生成和验证
    - 在表单提交中包含 CSRF token
    - _Requirements: 5.5_
  - [ ] 12.3 配置文件清理定时任务
    - 实现定时清理过期临时文件
    - 确保 10 分钟内删除处理完的文件
    - _Requirements: 5.2_

- [ ] 13. Final Checkpoint - 确保所有测试通过
  - Ensure all tests pass, ask the user if questions arise.
