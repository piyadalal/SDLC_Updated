import { route, fetch } from "@forge/api";

export async function handler(req) {
  const { requirement } = await req.json();

  const prompt = `
You are a senior agile product manager. Given the following requirement, generate:

- An Epic name
- 3–5 user stories in "As a ___, I want to ___ so that ___" format
- Acceptance Criteria for each story
- Notes like edge cases, test types, etc.

Output as a markdown table with columns: Epic | User Story | Acceptance Criteria | Notes

Requirement:
${requirement}
`;

  const endpoint = "https://2946-ai-project-management.openai.azure.com/";
  const deployment = "gpt-4o";
  const api_version = "2024-12-01-preview";

  const response = await fetch(
    route`${endpoint}openai/deployments/${deployment}/chat/completions?api-version=${api_version}`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "api-key": process.env.AZURE_OPENAI_API_KEY,
      },
      body: JSON.stringify({
        model: deployment,
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant that writes Jira-ready user stories and ACs."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        max_tokens: 2048,
        temperature: 0.6,
        top_p: 1.0
      })
    }
  );

  const data = await response.json();
  const table = data?.choices?.[0]?.message?.content || "No response received.";

  return new Response(JSON.stringify({ message: table }), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
}
