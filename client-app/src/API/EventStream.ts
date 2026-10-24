import { getToken } from '../auth/token.ts'
import { ApiError } from './ApiClient.ts'
import { API_URL } from './constants.ts'

export interface ServerEvent {
  event: string
  data: unknown
}

function parseEvent(block: string): ServerEvent | null {
  let event = 'message'
  const dataLines: string[] = []

  for (const line of block.split('\n')) {
    if (line.startsWith('event:')) event = line.slice(6).trim()
    else if (line.startsWith('data:')) dataLines.push(line.slice(5).trim())
  }

  if (dataLines.length === 0) return null
  return { event, data: JSON.parse(dataLines.join('\n')) }
}


export async function readEventStream(
  endpoint: string,
  onEvent: (event: ServerEvent) => void,
  signal: AbortSignal,
): Promise<void> {
  const token = getToken()
  const response = await fetch(`${API_URL.replace(/\/+$/, '')}${endpoint}`, {
    headers: {
      Accept: 'text/event-stream',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    signal,
  })

  if (!response.ok || !response.body) {
    const text = await response.text()
    throw new ApiError(response.status, text ? JSON.parse(text) : null)
  }

  const reader = response.body.pipeThrough(new TextDecoderStream()).getReader()
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) return

    buffer += value.replace(/\r\n/g, '\n')
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const event = parseEvent(block)
      if (event) onEvent(event)
    }
  }
}
