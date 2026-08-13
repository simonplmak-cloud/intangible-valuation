import { buildSystemPrompt } from "./prompts";

interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
}

interface ChatCompletionResponse {
  choices: { message: { content: string } }[];
}

const AI_API_URL = process.env.AI_API_URL ?? "https://api.deepseek.com/chat/completions";
const AI_MODEL = process.env.AI_MODEL ?? "deepseek-chat";

function getApiKey(): string | undefined {
  return process.env.AI_API_KEY ?? process.env.DEEPSEEK_API_KEY ?? process.env.PERPLEXITY_API_KEY;
}

/**
 * Model-agnostic chat completion. Defaults to DeepSeek (OpenAI-compatible);
 * any OpenAI-compatible endpoint can be used via AI_API_URL / AI_API_KEY.
 * Returns null when no key is configured so callers degrade gracefully.
 */
export async function advisorChat(
  history: ChatMessage[],
  onError?: (message: string) => void
): Promise<string | null> {
  const apiKey = getApiKey();
  if (!apiKey) {
    onError?.("AI advisor is not configured (missing AI_API_KEY).");
    return null;
  }

  const messages: ChatMessage[] = [{ role: "system", content: buildSystemPrompt() }, ...history];

  try {
    const res = await fetch(AI_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${apiKey}`,
      },
      body: JSON.stringify({ model: AI_MODEL, messages, temperature: 0.2, stream: false }),
    });

    if (!res.ok) {
      onError?.(`AI advisor error: ${res.status}`);
      return null;
    }

    const data = (await res.json()) as ChatCompletionResponse;
    return data.choices?.[0]?.message?.content ?? null;
  } catch (error) {
    onError?.(error instanceof Error ? error.message : "AI advisor failed");
    return null;
  }
}
