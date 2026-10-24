# 10. Scalability, Cost Economics & Technical Trade-Offs

## 1. Autoscaling Architecture (KEDA on Kubernetes)

The worker fleet scales elastically in response to queue pressure rather than CPU metrics, avoiding pipeline bottlenecks during viral traffic spikes:

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: premiere-render-worker-scaler
spec:
  scaleTargetRef:
    name: premiere-render-worker
  minReplicaCount: 1
  maxReplicaCount: 30
  triggers:
    - type: redis
      metadata:
        address: redis-cluster.internal:6379
        listName: queue:rendering-cluster
        listLength: "2" # Scales up 1 worker for every 2 pending render tasks
```

### Queue Priority Partitioning
- **`queue:high-priority`**: Subscribed/paying tier requests and interactive retries. Processed by dedicated warm worker replicas.
- **`queue:default-pipeline`**: Standard free-tier requests and scheduled batch jobs.
- **`queue:background-cleanup`**: Ephemeral asset deletion, CDN pre-warming, and telemetry aggregation.

---

## 2. Unit Economics: Cost Estimate Per 60s Video (1080p60)

| Pipeline Step | Provider / Resource | Consumption Metric | Unit Cost | Cost per 60s Video |
| :--- | :--- | :--- | :--- | :--- |
| **Repo & DOM Analysis** | Claude 3.5 Sonnet / GPT-4o | ~6,000 prompt tokens + ~1,200 output tokens | $3.00 / 1M prompt, $15.00 / 1M completion | **$0.0360** |
| **Browser Capture** | AWS Fargate / Hetzner (2 vCPU, 2GB RAM) | 45 seconds run time | $0.0405 / vCPU-hr, $0.0044 / GB-hr | **$0.0012** |
| **Audio Mastering** | CPU Worker (Librosa + FFmpeg) | 4 seconds processing | Negligible container slice | **$0.0003** |
| **Video Rendering** | Remotion Lambda (120 Lambdas x 15s) | 1,800 Lambda-seconds (3072MB RAM) | $0.00005 / GB-sec | **$0.1250** |
| **Object Storage** | Cloudflare R2 | ~250MB raw captures + ~45MB final MP4 (7-day retention) | $0.015 / GB-month | **$0.0010** |
| **Egress Bandwidth** | Cloudflare R2 | 2 downloads per video (~90MB) | $0.00 / GB egress | **$0.0000** |
| **Total Cost** | — | — | — | **~$0.1635 / Video** |

*Key Takeaway*: Rendering and LLM inference account for >98% of variable COGS. At **~$0.16 per video**, Premiere achieves incredible operating margins at standard SaaS subscription price points ($19 - $49/month).

---

## 3. Intelligent Render & Asset Caching

To prevent duplicate spending when users regenerate videos with minor tweaks:
1. **GitHub Commit SHA Caching**: If the user submits an identical GitHub repo URL and commit hash within 24 hours, the `ProductBriefJSON` is fetched directly from the database, skipping LLM analysis.
2. **Deterministic Capture Hashes**: If target URL routes have not changed, raw screenshots and screencasts are reused.
3. **Remotion Webpack Bundle Caching**: Pre-bundled Remotion compositions are cached in S3/Lambda layers, eliminating Webpack compile latency (saving ~12 seconds per render).

---

## 4. Key Architectural Trade-Off Analysis

### Trade-Off 1: Remotion Lambda vs. Self-Hosted Docker Workers

| Dimension | Remotion Lambda (AWS) | Self-Hosted Worker Pool (Docker / GPU) |
| :--- | :--- | :--- |
| **Render Speed (60s 1080p60)** | **15 - 25 seconds** (splits video across 100+ concurrent micro-lambdas). | **90 - 180 seconds** (single multi-core CPU node). |
| **Cold Start / Idle Cost** | **$0 idle cost**. Pays purely per millisecond of rendering. | Fixed baseline server costs ($100 - $400/month per GPU node). |
| **Operational Complexity** | Managed serverless execution via `@remotion/lambda`. | Requires Kubernetes autoscaling, Chromium GPU driver maintenance, and container zombie management. |
| **Decision** | **Remotion Lambda for Production; Self-Hosted Docker for Local Dev & CI.** |

---

### Trade-Off 2: Server-Sent Events (SSE) vs. WebSockets vs. Polling

| Protocol | Latency & UX | Overhead & Connection Cost | Reconnect & Proxy Compatibility |
| :--- | :--- | :--- | :--- |
| **Polling (`GET /jobs/{id}`)** | High latency (2-3s intervals); choppy UI progress. | Heavy HTTP handshake overhead on API gateway. | Works through all proxies; trivial to implement. |
| **WebSockets (`ws://`)** | Instantaneous two-way streaming. | Complex stateful connection management; sticky sessions required behind ALBs. | Frequent disconnects through corporate firewalls and edge CDNs. |
| **Server-Sent Events (SSE)** | **Instantaneous one-way stream (<50ms).** | **Lightweight HTTP/2 long-lived stream; standard FastAPI `StreamingResponse`.** | **Native browser `EventSource` with automated exponential backoff reconnects.** |
| **Decision** | **Server-Sent Events (SSE) as primary transport; polling as automatic client fallback.** |

---

### Trade-Off 3: Scene Plan Validation (Pydantic v2 + Instructor vs. LangChain)

| Evaluation Factor | Pydantic v2 + Instructor / Native Structured Outputs | LangChain / Heavy Agent Frameworks |
| :--- | :--- | :--- |
| **Schema Strictness** | Exact compile-time and runtime type validation; zero schema drift. | Prone to abstraction bloat, complex prompt wrapping, and breaking updates. |
| **Debugging & Transparency** | Pure standard Python classes; 10-minute junior engineer onboarding. | Multi-layer abstractions obscure exact API payloads and token overhead. |
| **Error Recovery** | Automatic retry validation loops on failed JSON schema checks. | Complex fallback chains with unpredictable latency. |
| **Decision** | **Pydantic v2 + Native Structured Outputs.** |
