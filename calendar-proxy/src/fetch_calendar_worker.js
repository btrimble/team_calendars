export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Map incoming path to your GitHub raw repo link
    // Example: https://your-worker.your-domain.workers.dev/soccer/premier_league/mancity.ics
    const githubRawBase = "https://raw.githubusercontent.com/btrimble/team_calendars/refs/heads/main/data";
    const githubUrl = githubRawBase + url.pathname;

    // Fetch the original file
    const response = await fetch(githubUrl);
    if (!response.ok) {
      return new Response("Not found", { status: 404 });
    }

    // Clone body but set new headers
    const icsBody = await response.text();
    const newHeaders = new Headers(response.headers);
		newHeaders.set("Content-Type", "text/calendar; charset=utf-8");
		newHeaders.set("Content-Disposition",
			`attachment; filename="${url.pathname.split('/').pop()}"; filename*=UTF-8''${url.pathname.split('/').pop()}`);
		newHeaders.set("Cache-Control", "public, max-age=3600");

    return new Response(icsBody, {
    	status: response.status,
      headers: newHeaders,
    });
  },
};
