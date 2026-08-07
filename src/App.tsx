import React from 'react';
import { FileUpload } from './components/FileUpload';
import { Chat } from './components/Chat';

function App() {
  return (
    <div style={{ maxWidth: '800px', margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h2>RAG Document Assistant</h2>
      <FileUpload />
      <Chat />
    </div>
  );
}

export default App;
