import { useChatStream } from './hooks/useChatStream';
import { MessageFeed } from './components/MessageFeed';
import { Header } from './components/Header';
import { ConnectorStatusBar } from './components/ConnectorStatusBar';

function App() {
  const { messages, statuses, connected } = useChatStream();

  return (
    <div className="flex h-full flex-col">
      <Header connected={connected} />
      <ConnectorStatusBar statuses={statuses} />
      <main className="flex-1 overflow-hidden">
        <MessageFeed messages={messages} />
      </main>
    </div>
  );
}

export default App;
