import { useEffect, useReducer, useRef, useState } from 'react';
import type { ChatMessage, Platform, WsServerMessage } from '@retrostudio/shared';

const WS_URL = import.meta.env.VITE_WS_URL ?? 'ws://localhost:3001/ws';

type ConnectorStatuses = Partial<Record<Platform, { connected: boolean; error?: string }>>;

type State = {
  messages: ChatMessage[];
  statuses: ConnectorStatuses;
};

type Action =
  | { type: 'chat'; payload: ChatMessage }
  | { type: 'connector_status'; payload: { platform: Platform; connected: boolean; error?: string } }
  | { type: 'reset' };

const MAX_MESSAGES = 500;

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'chat': {
      const next = [action.payload, ...state.messages];
      if (next.length > MAX_MESSAGES) next.length = MAX_MESSAGES;
      return { ...state, messages: next };
    }
    case 'connector_status':
      return {
        ...state,
        statuses: {
          ...state.statuses,
          [action.payload.platform]: {
            connected: action.payload.connected,
            error: action.payload.error,
          },
        },
      };
    case 'reset':
      return { messages: [], statuses: {} };
  }
}

export function useChatStream() {
  const [state, dispatch] = useReducer(reducer, { messages: [], statuses: {} });
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null;

    const connect = () => {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.addEventListener('open', () => {
        setConnected(true);
      });

      ws.addEventListener('close', () => {
        setConnected(false);
        // Reconectar a los 2s
        reconnectTimer = setTimeout(connect, 2000);
      });

      ws.addEventListener('message', (event) => {
        try {
          const msg = JSON.parse(event.data) as WsServerMessage;
          if (msg.type === 'chat' || msg.type === 'connector_status') {
            dispatch(msg);
          }
        } catch {
          // ignore parse errors
        }
      });
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, []);

  return { messages: state.messages, statuses: state.statuses, connected };
}
