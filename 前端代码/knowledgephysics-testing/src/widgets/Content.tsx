import React from 'react';
import Chat from './Chat';

const Content: React.FC = () => {
  return (
    <div className="flex flex-col p-4 h-screen">
      <div className="flex-1">
        <Chat />
      </div>
    </div>
  );
};

export default Content;