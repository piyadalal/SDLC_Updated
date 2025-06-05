import api, { route } from '@forge/api';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY; // Set this via Forge variables

export async function handler({ event }) {
  // const pageId = event?.payload?.pageId;
  const pageId = 66354;
  console.log('Received pageId:', pageId);
  if (!pageId) {
    throw new Error('Missing pageId in payload');
  }
  // Step 1: Get the page content
  const pageRes = await api.asApp().requestConfluence(route`/wiki/api/v2/pages/${pageId}`);
  const pageData = await pageRes.json();
  const title = pageData.title;

  const bodyRes = await api.asApp().requestConfluence(
    route`/wiki/api/v2/pages/${pageId}?body-format=storage`
  );
  const bodyData = await bodyRes.json();

  const requirementText = bodyData.body?.storage?.value?.replace(/<[^>]*>?/gm, '') || '';


  // Step 2: Call GPT (stubbed here)
  const gptResponse = await callGPT(requirementText); // Placeholder

  // Step 3: Create table (ADF format)
  const tableADF = generateADFTable(gptResponse);

  // Step 4: Create new Confluence page
  const newPage = await api.asApp().requestConfluence(route`/wiki/api/v2/pages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      title: `Breakdown of ${title}`,
      type: 'page',
      spaceId: pageData.spaceId,
      body: {
        atlas_doc_format: {
          value: JSON.stringify(tableADF),
          representation: 'atlas_doc_format'
        }
      }
    })
  });

  return { ok: true };
}

async function callGPT(requirementText) {
  const endpoint = 'https://2946-ai-project-manager.openai.azure.com/';
  const apiKey = process.env.AZURE_OPENAI_KEY;
  const apiVersion = '2024-12-01-preview';
  const deployment = 'gpt-4o';

  const url = `${endpoint}openai/deployments/${deployment}/chat/completions?api-version=${apiVersion}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'api-key': apiKey
    },
    body: JSON.stringify({
      messages: [
        {
          role: 'system',
          content: 'You are a senior agile product manager assistant. Given the following requirement text, generate a structured breakdown as a JSON array of objects. Each object should have: epic, story, ac, category, notes (leave notes blank).'
        },
        {
          role: 'user',
          content: requirementText
        }
      ],
      temperature: 0.7,
      max_tokens: 1500
    })
  });

  const json = await response.json();

  if (!response.ok) {
    console.error('OpenAI API Error:', json);
    throw new Error(json.error?.message || 'Failed to call OpenAI');
  }
  if (response.status !== 200) {
  const errorText = await response.text();
  console.error('Raw OpenAI error text:', errorText);
}


  const assistantReply = json.choices[0]?.message?.content;

  try {
    return JSON.parse(assistantReply);
  } catch (e) {
    console.error('Failed to parse GPT response:', assistantReply);
    throw new Error('GPT returned invalid JSON. You may need to tweak the prompt or validate manually.');
  }
}


function generateADFTable(data) {
  const headers = ['Epic', 'User Story', 'AC', 'Category', 'Notes'];
  const rows = data.map(item => [
    item.epic, item.story, item.ac, item.category, item.notes
  ]);

  return {
    type: 'doc',
    version: 1,
    content: [
      {
        type: 'table',
        content: [
          {
            type: 'tableRow',
            content: headers.map(header => ({
              type: 'tableHeader',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: header }] }]
            }))
          },
          ...rows.map(row => ({
            type: 'tableRow',
            content: row.map(cell => ({
              type: 'tableCell',
              content: [{ type: 'paragraph', content: [{ type: 'text', text: cell }] }]
            }))
          }))
        ]
      }
    ]
  };
}
