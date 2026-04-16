import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { getPromptsByKbName } from '../prompts';
import { APP_BASE_PATH } from '../config/paths';

interface Message {
  type: 'user' | 'system';
  content: string;
}

interface SearchResult {
  id: string;
  text: string;
  source: string;
}

const KB_NAME = "physics_kb"; // 与KnowledgeBase组件使用相同的知识库名称

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [useKnowledgeBase, setUseKnowledgeBase] = useState(true);
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (shouldAutoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 1;
    setShouldAutoScroll(isAtBottom);
  };

  const searchKnowledgeBase = async (query: string): Promise<SearchResult[]> => {
    try {
      const response = await fetch('/vecsearch/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query,
          kb_name: KB_NAME,
          top_k: 1
        })
      });

      if (!response.ok) {
        throw new Error('知识库搜索失败');
      }

      const data = await response.json();
      if (data.scores.length > 0 && data.scores[0] > 1.0) {
        return [];
      }
      return data.results || [];
    } catch (error) {
      console.error('知识库搜索失败:', error);
      return [];
    }
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      type: 'user',
      content: inputValue.trim()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // 获取当前知识库对应的 prompts
      const { systemPrompt, userPrompt } = getPromptsByKbName(KB_NAME);
      
      // 如果启用了知识库，先搜索相关内容
      let contextContent = '';
      if (useKnowledgeBase) {
        const searchResults = await searchKnowledgeBase(userMessage.content);
        if (searchResults.length > 0) {
          contextContent = searchResults.map(result => 
            `${result.text} (来源: ${result.source})`
          ).join('\\n');

          contextContent = "参考资料：" + contextContent
        }
      }

      // 替换 prompt 中的占位符
      const finalSystemPrompt = systemPrompt;
      const finalUserPrompt = userPrompt
        .replace('{retrieved_context}', contextContent)
        .replace('{user_question}', userMessage.content)
        .replace('{user_case_example}', userMessage.content);

      const response = await fetch('https://innoflow.study.sensetime.com/v1/agents/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          systemPrompt: finalSystemPrompt,
          query: finalUserPrompt,
          model: "DEEPSEEK_V3"
        })
      });

      if (!response.body) throw new Error('No response body');

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let systemMessage: Message = {
        type: 'system',
        content: ''
      };
      setMessages(prev => [...prev, systemMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.delta && data.delta !== '[DONE]') {
                systemMessage.content += data.delta;
                setMessages(prev => prev.map((msg, i) => 
                  i === prev.length - 1 ? { ...msg, content: systemMessage.content } : msg
                ));
              }
            } catch (e) {
              console.error('Failed to parse chunk:', e);
            }
          }
        }
      }
    } catch (error) {
      const errorMessage: Message = {
        type: 'system',
        content: '抱歉，服务器出现问题，请稍后再试。'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-b from-gray-50 to-white rounded-xl shadow-lg border border-gray-100">
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-full flex items-center justify-center ">
            <img src={`${APP_BASE_PATH}/images/icon.png`} alt="AI" className="w-full h-full object-cover rounded-full" />
          </div>
          <h1 className="text-xl font-semibold text-gray-800">AI物理学科问答系统</h1>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">知识库</span>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={useKnowledgeBase}
              onChange={(e) => setUseKnowledgeBase(e.target.checked)}
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      {/* 消息列表 */}
      <div 
        className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth bg-gray-50"
        onScroll={handleScroll}
      >
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} items-start gap-3`}
          >
            {message.type === 'system' && (
              <div className="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center mt-1 overflow-hidden">
                <img src={`${APP_BASE_PATH}/images/ai_icon.png`} alt="AI" className="w-full h-full object-cover" />
              </div>
            )}
            <div
              className={`max-w-[80%] ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white rounded-2xl rounded-tr-sm ml-auto' 
                  : 'bg-white text-gray-700 shadow-sm border border-gray-200 rounded-2xl rounded-tl-sm'
              } px-6 py-4`}
            >
              {message.type === 'user' ? (
                <p className="text-sm leading-relaxed text-left">{message.content}</p>
              ) : (
                <div className="prose prose-sm max-w-none dark:prose-invert text-left">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>
              )}
            </div>
            {message.type === 'user' && (
              <div className="w-8 h-8 rounded-lg flex-shrink-0 flex items-center justify-center mt-1 overflow-hidden">
                <img src={`${APP_BASE_PATH}/images/user_icon.png`} alt="User" className="w-full h-full object-cover" />
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 输入区域 */}
      <div className="border-t border-gray-200 p-6 bg-white">
        <div className="relative">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="输入您的问题..."
            className="w-full pl-4 pr-24 py-4 text-gray-700 bg-white rounded-xl resize-none focus:outline-none 
            focus:ring-2 focus:ring-blue-500 border border-gray-200/80 hover:border-gray-300/80 transition-colors shadow-sm"
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={isLoading || !inputValue.trim()}
            className={`absolute right-2 top-1/2 -translate-y-1/2 flex items-center justify-center gap-2 px-4 
              py-2 bg-blue-500 text-white rounded-lg
               hover:bg-blue-600 transition-colors disabled:opacity-50
                disabled:cursor-not-allowed ${isLoading ? 'cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {isLoading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 
                014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
            )}
            {isLoading ? '发送中...' : '发送'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chat;