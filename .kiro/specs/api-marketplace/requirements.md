# Requirements Document

## Introduction

API 商店是一个按调用收费的 API 服务平台，允许开发者通过 API Key 调用各种实用工具 API。系统提供免费额度（1000次/月），超出后需要订阅付费套餐。API 包括文本清洗、时间格式化、网页信息提取、图片压缩和自然语言处理等功能。

## Glossary

- **API_Marketplace**: API 商店系统，提供 API 服务和计费管理
- **API_Key**: 用于身份验证的唯一密钥，格式为 `ak_` 前缀加32位随机字符
- **Usage_Tracker**: 使用量追踪器，记录每个 API Key 的调用次数
- **Subscription_Plan**: 订阅计划，定义免费额度和付费套餐
- **Rate_Limiter**: 速率限制器，控制 API 调用频率
- **Text_Cleaner**: 文本清洗服务，去除符号、去重、标准化文本
- **Date_Formatter**: 日期格式化服务，转换各种日期时间格式
- **Web_Scraper**: 网页信息提取服务，获取网页标题、描述、元数据
- **NLP_Processor**: 自然语言处理服务，提供关键词提取和文本摘要

## Requirements

### Requirement 1: API Key 管理

**User Story:** As a developer, I want to generate and manage API keys, so that I can securely access the API services.

#### Acceptance Criteria

1. WHEN a user requests a new API key THEN the API_Marketplace SHALL generate a unique key with `ak_` prefix followed by 32 random alphanumeric characters
2. WHEN an API key is generated THEN the API_Marketplace SHALL store the key hash, creation timestamp, and associated user ID
3. WHEN a user requests to revoke an API key THEN the API_Marketplace SHALL mark the key as inactive and reject subsequent requests using that key
4. WHEN an API request includes an invalid or revoked key THEN the API_Marketplace SHALL return HTTP 401 with error message "Invalid API key"
5. WHEN an API key is used THEN the API_Marketplace SHALL validate the key format before checking the database

### Requirement 2: 使用量追踪

**User Story:** As a developer, I want to track my API usage, so that I can monitor consumption and plan accordingly.

#### Acceptance Criteria

1. WHEN an API call succeeds THEN the Usage_Tracker SHALL increment the monthly usage counter for that API key
2. WHEN a user queries usage statistics THEN the Usage_Tracker SHALL return current month usage, remaining quota, and historical usage data
3. WHEN a new month begins THEN the Usage_Tracker SHALL reset the monthly usage counter to zero while preserving historical records
4. WHEN usage data is recorded THEN the Usage_Tracker SHALL store timestamp, endpoint, response time, and status code

### Requirement 3: 订阅计划与计费

**User Story:** As a developer, I want to choose a subscription plan, so that I can access API services within my budget.

#### Acceptance Criteria

1. THE API_Marketplace SHALL provide a free tier with 1000 API calls per month
2. THE API_Marketplace SHALL provide paid tiers: Basic (￥9.9/month, 10000 calls), Pro (￥19.9/month, 50000 calls), Enterprise (￥29.9/month, unlimited calls)
3. WHEN a user exceeds their monthly quota THEN the API_Marketplace SHALL return HTTP 429 with error message "Quota exceeded" and include upgrade information
4. WHEN a user upgrades their plan THEN the API_Marketplace SHALL immediately apply the new quota limits
5. WHEN a subscription expires THEN the API_Marketplace SHALL downgrade the user to free tier

### Requirement 4: 文本清洗 API

**User Story:** As a developer, I want to clean and normalize text data, so that I can process user input consistently.

#### Acceptance Criteria

1. WHEN the Text_Cleaner receives text with special symbols THEN the Text_Cleaner SHALL remove or replace symbols based on the specified mode (remove_all, keep_punctuation, custom_pattern)
2. WHEN the Text_Cleaner receives text with duplicate lines THEN the Text_Cleaner SHALL remove duplicates while preserving original order
3. WHEN the Text_Cleaner receives text with mixed whitespace THEN the Text_Cleaner SHALL normalize to single spaces and trim leading/trailing whitespace
4. WHEN the Text_Cleaner processes text THEN the Text_Cleaner SHALL return the cleaned text and a summary of changes made
5. WHEN the Text_Cleaner receives empty input THEN the Text_Cleaner SHALL return empty string without error

### Requirement 5: 日期时间格式化 API

**User Story:** As a developer, I want to convert date/time formats, so that I can standardize timestamps across systems.

#### Acceptance Criteria

1. WHEN the Date_Formatter receives a date string and target format THEN the Date_Formatter SHALL convert to the specified format (ISO8601, Unix timestamp, RFC2822, custom pattern)
2. WHEN the Date_Formatter receives a Unix timestamp THEN the Date_Formatter SHALL convert to human-readable format in the specified timezone
3. WHEN the Date_Formatter receives an ambiguous date THEN the Date_Formatter SHALL use the specified locale rules or return error with suggestions
4. WHEN the Date_Formatter receives an invalid date THEN the Date_Formatter SHALL return HTTP 400 with parsing error details
5. WHEN the Date_Formatter processes a date THEN the Date_Formatter SHALL include original input, parsed interpretation, and formatted output in response

### Requirement 6: 网页信息提取 API

**User Story:** As a developer, I want to extract metadata from web pages, so that I can build link previews and content aggregators.

#### Acceptance Criteria

1. WHEN the Web_Scraper receives a URL THEN the Web_Scraper SHALL extract title, description, Open Graph tags, and favicon URL
2. WHEN the Web_Scraper encounters a redirect THEN the Web_Scraper SHALL follow up to 5 redirects and return the final URL
3. WHEN the Web_Scraper cannot access a URL THEN the Web_Scraper SHALL return HTTP 502 with the specific error (timeout, DNS failure, connection refused)
4. WHEN the Web_Scraper extracts content THEN the Web_Scraper SHALL complete within 10 seconds or return timeout error
5. WHEN the Web_Scraper receives a non-HTML response THEN the Web_Scraper SHALL return content type and size without attempting HTML parsing

### Requirement 7: 图片压缩 API

**User Story:** As a developer, I want to compress images via API, so that I can optimize images in my application pipeline.

#### Acceptance Criteria

1. WHEN the Image_Compressor receives an image THEN the Image_Compressor SHALL compress to the specified quality level (1-100) or target file size
2. WHEN the Image_Compressor processes an image THEN the Image_Compressor SHALL preserve EXIF data if requested, or strip it by default
3. WHEN the Image_Compressor receives an unsupported format THEN the Image_Compressor SHALL return HTTP 400 listing supported formats (JPEG, PNG, WebP, GIF)
4. WHEN compression completes THEN the Image_Compressor SHALL return the compressed image and metadata (original size, compressed size, compression ratio)
5. WHEN the input image exceeds 10MB THEN the Image_Compressor SHALL return HTTP 413 with size limit information

### Requirement 8: 自然语言处理 API

**User Story:** As a developer, I want to extract keywords and generate summaries, so that I can analyze text content programmatically.

#### Acceptance Criteria

1. WHEN the NLP_Processor receives text for keyword extraction THEN the NLP_Processor SHALL return top N keywords with relevance scores
2. WHEN the NLP_Processor receives text for summarization THEN the NLP_Processor SHALL generate a summary within the specified length limit
3. WHEN the NLP_Processor receives text shorter than 50 characters THEN the NLP_Processor SHALL return the original text as the summary
4. WHEN the NLP_Processor processes text THEN the NLP_Processor SHALL support Chinese and English languages
5. WHEN the NLP_Processor receives unsupported language THEN the NLP_Processor SHALL return HTTP 400 with detected language and supported language list

### Requirement 9: API 速率限制

**User Story:** As a system administrator, I want to limit API request rates, so that the system remains stable under high load.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL enforce per-minute limits based on subscription tier (Free: 60/min, Basic: 120/min, Pro: 300/min, Enterprise: 1000/min)
2. WHEN a request exceeds the rate limit THEN the Rate_Limiter SHALL return HTTP 429 with Retry-After header indicating seconds until reset
3. WHEN rate limit headers are returned THEN the Rate_Limiter SHALL include X-RateLimit-Limit, X-RateLimit-Remaining, and X-RateLimit-Reset headers
4. WHEN a burst of requests arrives THEN the Rate_Limiter SHALL use sliding window algorithm to smooth traffic

### Requirement 10: API 文档与开发者门户

**User Story:** As a developer, I want comprehensive API documentation, so that I can integrate the APIs quickly.

#### Acceptance Criteria

1. THE API_Marketplace SHALL provide OpenAPI 3.0 specification for all endpoints
2. THE API_Marketplace SHALL provide interactive API playground for testing endpoints
3. WHEN a user views documentation THEN the API_Marketplace SHALL display request/response examples in multiple languages (curl, Python, JavaScript, Java)
4. THE API_Marketplace SHALL provide SDK download links for Python and JavaScript

### Requirement 11: 安全性

**User Story:** As a developer, I want secure API access, so that my data and credentials are protected.

#### Acceptance Criteria

1. THE API_Marketplace SHALL transmit all API traffic over HTTPS only
2. WHEN storing API keys THEN the API_Marketplace SHALL hash keys using SHA-256 before storage
3. WHEN an API key shows suspicious activity THEN the API_Marketplace SHALL temporarily suspend the key and notify the owner
4. THE API_Marketplace SHALL log all API requests with anonymized client information for security auditing
