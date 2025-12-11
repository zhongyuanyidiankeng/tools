# Requirements Document

## Introduction

本项目是一个轻量级在线工具平台，旨在通过 SEO 获取被动流量并通过广告变现。平台提供 PDF 处理、图像处理、文本工具和开发者工具等实用功能。系统设计为可在 1G 内存小型服务器上稳定运行，使用 Python 处理核心工具逻辑，Java (Spring Boot) 提供稳定 API 服务。

## Glossary

- **Tool_Platform**: 在线工具平台系统，提供各类实用工具的 Web 应用
- **Tool_Service**: 处理具体工具功能的后端服务模块
- **User**: 访问平台使用工具的终端用户
- **API_Gateway**: 统一管理 API 请求的入口服务
- **File_Processor**: 处理用户上传文件的组件

## Requirements

### Requirement 1: PDF 工具功能

**User Story:** As a user, I want to process PDF files online, so that I can quickly compress, convert, merge or split PDF documents without installing software.

#### Acceptance Criteria

1. WHEN a user uploads a PDF file for compression THEN the Tool_Service SHALL reduce the file size by at least 30% while maintaining readable quality
2. WHEN a user uploads a PDF file for conversion to Word THEN the Tool_Service SHALL generate a downloadable DOCX file within 60 seconds
3. WHEN a user uploads multiple PDF files for merging THEN the Tool_Service SHALL combine the files in the specified order and return a single PDF
4. WHEN a user uploads a PDF file for splitting THEN the Tool_Service SHALL allow page range selection and generate separate PDF files
5. WHEN a user uploads images for PDF conversion THEN the Tool_Service SHALL create a PDF containing all images in upload order
6. IF a user uploads a file exceeding 10MB THEN the Tool_Service SHALL reject the upload and display a clear size limit message

### Requirement 2: 图像处理功能

**User Story:** As a user, I want to process images online, so that I can compress, convert, resize, or split images without specialized software.

#### Acceptance Criteria

1. WHEN a user uploads an image for compression THEN the Tool_Service SHALL reduce file size while maintaining visual quality above 80%
2. WHEN a user uploads an image and specifies a target file size THEN the Tool_Service SHALL compress the image to meet the specified size limit
3. WHEN a user uploads a WebP image for JPG conversion THEN the Tool_Service SHALL generate a valid JPG file
4. WHEN a user uploads an image for cropping THEN the Tool_Service SHALL provide dimension input fields and generate the cropped result
5. WHEN a user uploads an image for grid splitting THEN the Tool_Service SHALL display draggable split lines for row and column configuration
6. WHEN a user adjusts grid split lines THEN the Tool_Service SHALL show real-time preview of the resulting grid sections
7. WHEN a user confirms grid splitting THEN the Tool_Service SHALL generate separate image files for each grid section
8. WHEN a user selects split-and-compress mode THEN the Tool_Service SHALL split the image into grid sections and compress each section to the specified size
9. WHEN a user uploads an image for ICO generation THEN the Tool_Service SHALL create a valid ICO file with standard icon dimensions
10. IF a user uploads an unsupported image format THEN the Tool_Service SHALL display a list of supported formats

### Requirement 3: 文本工具功能

**User Story:** As a user, I want to use text processing tools online, so that I can format, encode, or test text data quickly.

#### Acceptance Criteria

1. WHEN a user inputs JSON text for formatting THEN the Tool_Service SHALL return properly indented and validated JSON
2. WHEN a user inputs text for Base64 encoding THEN the Tool_Service SHALL return the encoded string immediately
3. WHEN a user inputs Base64 text for decoding THEN the Tool_Service SHALL return the decoded original text
4. WHEN a user inputs a regex pattern and test string THEN the Tool_Service SHALL highlight all matches and display match groups
5. WHEN a user inputs Markdown text THEN the Tool_Service SHALL render and display the HTML preview
6. IF a user inputs invalid JSON for formatting THEN the Tool_Service SHALL display the specific syntax error location

### Requirement 4: 开发者工具功能

**User Story:** As a developer, I want to use developer-focused utilities online, so that I can quickly decode tokens, generate identifiers, or test expressions.

#### Acceptance Criteria

1. WHEN a user inputs a JWT token THEN the Tool_Service SHALL decode and display the header, payload, and signature status
2. WHEN a user selects cron expression options THEN the Tool_Service SHALL generate the corresponding cron string and display next execution times
3. WHEN a user requests UUID generation THEN the Tool_Service SHALL generate a valid UUID v4 and provide copy functionality
4. WHEN a user queries an IP address THEN the Tool_Service SHALL return geolocation and ISP information

### Requirement 5: 文件上传与安全

**User Story:** As a platform operator, I want secure file handling, so that the system remains safe and resources are protected.

#### Acceptance Criteria

1. WHEN a user uploads a file THEN the Tool_Platform SHALL validate file type by content inspection rather than extension only
2. WHEN a file is processed THEN the Tool_Platform SHALL delete the file from server within 10 minutes
3. WHILE processing user files THEN the Tool_Platform SHALL isolate each request to prevent cross-user data access
4. IF a request exceeds rate limits THEN the Tool_Platform SHALL return a 429 status with retry-after information
5. WHEN serving tool pages THEN the Tool_Platform SHALL implement CSRF protection on all form submissions

### Requirement 6: 性能与资源管理

**User Story:** As a platform operator, I want efficient resource usage, so that the platform runs stably on a 1GB memory server.

#### Acceptance Criteria

1. WHILE the server is running THEN the Tool_Platform SHALL maintain memory usage below 800MB under normal load
2. WHEN processing files THEN the Tool_Service SHALL use streaming processing for files larger than 5MB
3. WHEN multiple requests arrive simultaneously THEN the Tool_Platform SHALL queue requests exceeding 3 concurrent processing tasks
4. IF server memory exceeds 900MB THEN the Tool_Platform SHALL reject new file processing requests temporarily

### Requirement 7: SEO 与页面结构

**User Story:** As a platform operator, I want SEO-optimized pages, so that the tools can be discovered through search engines.

#### Acceptance Criteria

1. WHEN rendering a tool page THEN the Tool_Platform SHALL include unique meta title, description, and canonical URL
2. WHEN rendering tool pages THEN the Tool_Platform SHALL generate semantic HTML with proper heading hierarchy
3. WHEN the sitemap is requested THEN the Tool_Platform SHALL return an up-to-date XML sitemap of all tool pages
4. WHEN a tool page loads THEN the Tool_Platform SHALL achieve a Lighthouse performance score above 80

### Requirement 8: 广告集成

**User Story:** As a platform operator, I want to display advertisements, so that the platform can generate passive income from traffic.

#### Acceptance Criteria

1. WHEN a tool page loads THEN the Tool_Platform SHALL display ad placements without blocking tool functionality
2. WHEN rendering ads THEN the Tool_Platform SHALL load ad scripts asynchronously to avoid blocking page render
3. WHILE displaying ads THEN the Tool_Platform SHALL maintain tool usability on mobile devices
