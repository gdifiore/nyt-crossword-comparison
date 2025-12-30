# API Documentation

## Base URL

```
Production: https://your-app-name.herokuapp.com
Development: http://localhost:5000
```

## Rate Limiting

- Global: 200 requests/day, 50 requests/hour per IP
- `POST /api/data`: 1 request/day per IP
- `GET /api/chartData`: 10 requests/minute per IP

Rate limit exceeded returns `429 Too Many Requests`.

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "Human-readable error message"
}
```

## Endpoints

### POST /api/data

Submit completion time.

**Rate Limit:** 1 request per IP per day

**Request Body:**

```json
{
  "secondsToComplete": 123
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| secondsToComplete | integer | Yes | Completion time in seconds (10-900) |

**Validation Rules:**

- Must be an integer
- Minimum: 10 seconds
- Maximum: 900 seconds (15 minutes)

**Success Response:**

```json
{
  "message": "Data received successfully"
}
```

**Status Code:** `200 OK`

**Error Responses:**

| Status | Error | Reason |
|--------|-------|--------|
| 400 | "Invalid data: missing secondsToComplete" | Request missing required field |
| 400 | "Invalid data: secondsToComplete must be an integer" | Field is not an integer |
| 400 | "Invalid time: X seconds is too fast. Minimum is 10 seconds." | Time below minimum |
| 400 | "Invalid time: X seconds is too slow. Maximum is 900 seconds (15 minutes)." | Time above maximum |
| 429 | Rate limit error | Already submitted today |
| 500 | "Failed to save data. Please try again." | Database error |

**Example Request:**

```bash
curl -X POST https://your-app-name.herokuapp.com/api/data \
  -H "Content-Type: application/json" \
  -d '{"secondsToComplete": 95}'
```

**Example Success Response:**

```json
{
  "message": "Data received successfully"
}
```

**Example Error Response:**

```json
{
  "error": "Invalid time: 5 seconds is too fast. Minimum is 10 seconds."
}
```

---

### GET /api/chartData

Returns histogram bins for today's submissions.

**Rate Limit:** 10 requests per minute

**Request:** No parameters required

**Success Response:**

```json
{
  "data": [
    {
      "range": "0:45-1:15",
      "count": 12
    },
    {
      "range": "1:15-1:45",
      "count": 25
    },
    {
      "range": "1:45-2:15",
      "count": 18
    }
  ]
}
```

**Status Code:** `200 OK`

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| data | array | Histogram bins |
| data[].range | string | Time range (MM:SS-MM:SS) |
| data[].count | integer | Submissions in bin |

**Notes:**

- Bins: 3-15 adaptive bins based on data spread
- Empty array if no data

**Error Responses:**

| Status | Error | Reason |
|--------|-------|--------|
| 429 | Rate limit error | Too many requests |
| 500 | "Failed to load chart data" | Database or calculation error |

**Example Request:**

```bash
curl https://your-app-name.herokuapp.com/api/chartData
```

**Example Response:**

```json
{
  "data": [
    {"range": "0:30-0:50", "count": 8},
    {"range": "0:50-1:10", "count": 15},
    {"range": "1:10-1:30", "count": 22},
    {"range": "1:30-1:50", "count": 19},
    {"range": "1:50-2:10", "count": 11}
  ]
}
```

---

### GET /api/stats

Returns today's stats and last 30 days of historical data.

**Rate Limit:** Global rate limits apply

**Request:** No parameters required

**Success Response:**

```json
{
  "today": {
    "count": 42,
    "avg_time": 125.5,
    "min_time": 45,
    "max_time": 320
  },
  "historical": [
    {
      "date": "2024-01-15",
      "count": 38,
      "avg_time": 132.8,
      "min_time": 50,
      "max_time": 280
    }
  ]
}
```

**Status Code:** `200 OK`

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| today.count | integer | Number of submissions today |
| today.avg_time | float | Average completion time in seconds |
| today.min_time | integer | Fastest time in seconds |
| today.max_time | integer | Slowest time in seconds |
| historical | array | Last 30 days of archived data |
| historical[].date | string | Date in YYYY-MM-DD format |
| historical[].count | integer | Number of submissions that day |
| historical[].avg_time | float | Average time in seconds |
| historical[].min_time | integer | Fastest time in seconds |
| historical[].max_time | integer | Slowest time in seconds |

**Notes:**

- Historical data populated by daily `clear_db.py` script
- Ordered by date descending

**Error Responses:**

| Status | Error | Reason |
|--------|-------|--------|
| 500 | "Failed to load statistics" | Database error |

**Example Request:**

```bash
curl https://your-app-name.herokuapp.com/api/stats
```

**Example Response:**

```json
{
  "today": {
    "count": 156,
    "avg_time": 142.3,
    "min_time": 38,
    "max_time": 450
  },
  "historical": [
    {
      "date": "2024-01-14",
      "count": 143,
      "avg_time": 138.7,
      "min_time": 42,
      "max_time": 420
    },
    {
      "date": "2024-01-13",
      "count": 128,
      "avg_time": 145.2,
      "min_time": 45,
      "max_time": 380
    }
  ]
}
```

---

### GET /api/health

Service health and database status.

**Rate Limit:** Global rate limits apply

**Request:** No parameters required

**Success Response:**

```json
{
  "status": "healthy",
  "service": "nyt-crossword-comparison",
  "version": "0.0.1",
  "timestamp": "2024-01-15T12:34:56.789012",
  "database": "connected",
  "database_pool": {
    "min_connections": 1,
    "max_connections": 10
  }
}
```

**Status Code:** `200 OK`

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| status | string | "healthy" or "unhealthy" |
| service | string | Service name |
| version | string | Application version |
| timestamp | string | ISO 8601 timestamp |
| database | string | "connected" or "disconnected" |
| database_pool.min_connections | integer | Min pool size |
| database_pool.max_connections | integer | Max pool size |

**Unhealthy Response:**

```json
{
  "status": "unhealthy",
  "service": "nyt-crossword-comparison",
  "version": "0.0.1",
  "timestamp": "2024-01-15T12:34:56.789012",
  "database": "disconnected",
  "error": "connection refused"
}
```

**Status Code:** `503 Service Unavailable`

**Example Request:**

```bash
curl https://your-app-name.herokuapp.com/api/health
```

**Example Response:**

```json
{
  "status": "healthy",
  "service": "nyt-crossword-comparison",
  "version": "0.0.1",
  "timestamp": "2024-01-15T14:23:45.123456",
  "database": "connected",
  "database_pool": {
    "min_connections": 1,
    "max_connections": 10
  }
}
```

---

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input data |
| 404 | Not Found | Endpoint does not exist |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server-side error |
| 503 | Service Unavailable | Service is unhealthy |

## Data Lifecycle

- `puzzle_completion` table cleared daily at midnight UTC
- Data archived to `puzzle_completion_archive` before clearing
- Archive accessible via `/api/stats` endpoint
