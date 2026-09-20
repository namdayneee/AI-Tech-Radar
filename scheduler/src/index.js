// ============================================================
// AI TECH RADAR
// CLOUDFLARE SCHEDULER
// ============================================================


// ============================================================
// CRON → GITHUB WORKFLOW
// ============================================================

const JOBS = {

    // 06:45 Việt Nam
    "45 23 * * *":
      "collect-news.yml",
  
  
    // 07:30 Việt Nam
    "30 0 * * *":
      "daily-digest.yml",
  
  
    // 03:00 Chủ Nhật Việt Nam
    "0 20 * * 6":
      "cleanup.yml",
  };
  
  
  // ============================================================
  // FRIENDLY NAMES
  // ============================================================
  
  const LABELS = {
  
    "collect-news.yml":
      "Collect AI Tech News",
  
    "daily-digest.yml":
      "Send Daily AI Tech Digest",
  
    "cleanup.yml":
      "Cleanup Old AI Tech Articles",
  };
  
  
  // ============================================================
  // SLEEP
  // ============================================================
  
  function sleep(ms) {
  
    return new Promise(
      (resolve) =>
        setTimeout(resolve, ms)
    );
  }
  
  
  // ============================================================
  // GITHUB DISPATCH
  // ============================================================
  
  async function dispatchWorkflow(
    workflowFile,
    env,
  ) {
  
    if (!env.GITHUB_TOKEN) {
  
      throw new Error(
        "Missing GITHUB_TOKEN"
      );
    }
  
  
    if (
      !env.GITHUB_OWNER
      || !env.GITHUB_REPO
    ) {
  
      throw new Error(
        "Missing GitHub repository config"
      );
    }
  
  
    const owner =
      encodeURIComponent(
        env.GITHUB_OWNER
      );
  
  
    const repo =
      encodeURIComponent(
        env.GITHUB_REPO
      );
  
  
    const workflow =
      encodeURIComponent(
        workflowFile
      );
  
  
    const ref =
      env.GITHUB_REF
      || "main";
  
  
    const url =
      `https://api.github.com/`
      + `repos/${owner}/${repo}/`
      + `actions/workflows/`
      + `${workflow}/dispatches`;
  
  
    let lastError = null;
  
  
    // ==========================================================
    // Retry 3 lần
    // ==========================================================
  
    for (
      let attempt = 1;
      attempt <= 3;
      attempt++
    ) {
  
      try {
  
        const response =
          await fetch(
            url,
            {
  
              method: "POST",
  
              headers: {
  
                "Accept":
                  "application/vnd.github+json",
  
                "Authorization":
                  `Bearer ${env.GITHUB_TOKEN}`,
  
                "X-GitHub-Api-Version":
                  "2022-11-28",
  
                "User-Agent":
                  "ai-tech-radar-cloudflare-scheduler",
  
                "Content-Type":
                  "application/json",
              },
  
  
              body: JSON.stringify(
                {
                  ref: ref,
                }
              ),
            }
          );
  
  
        const body =
          await response.text();
  
  
        if (!response.ok) {
  
          throw new Error(
            `GitHub API error `
            + `${response.status}: `
            + body
          );
        }
  
  
        console.log(
          `[OK] ${
            LABELS[workflowFile]
            || workflowFile
          } dispatched`
        );
  
  
        return;
  
      }
  
      catch (error) {
  
        lastError = error;
  
  
        console.error(
          `[WARN] Dispatch `
          + `${attempt}/3 failed: `
          + error.message
        );
  
  
        if (attempt < 3) {
  
          await sleep(
            attempt * 1000
          );
        }
      }
    }
  
  
    throw lastError;
  }
  
  
  // ============================================================
  // WORKER
  // ============================================================
  
  export default {
  
  
    // ==========================================================
    // CRON HANDLER
    // ==========================================================
  
    async scheduled(
      controller,
      env,
      ctx,
    ) {
  
      const workflowFile =
        JOBS[
          controller.cron
        ];
  
  
      if (!workflowFile) {
  
        console.warn(
          `[SKIP] Unknown cron: `
          + controller.cron
        );
  
        return;
      }
  
  
      ctx.waitUntil(
        dispatchWorkflow(
          workflowFile,
          env,
        )
      );
    },
  
  
    // ==========================================================
    // HTTP STATUS
    // ==========================================================
  
    async fetch(
      request,
    ) {
  
      const url =
        new URL(
          request.url
        );
  
  
      if (
        url.pathname !== "/"
      ) {
  
        return new Response(
          "Not found",
          {
            status: 404,
          }
        );
      }
  
  
      return Response.json({
  
        service:
          "AI Tech Radar Scheduler",
  
        status:
          "ok",
  
        timezone:
          "Asia/Ho_Chi_Minh",
  
        schedules: {
  
          collect:
            "06:45",
  
          digest:
            "07:30",
  
          cleanup:
            "Sunday 03:00",
        },
      });
    },
  };