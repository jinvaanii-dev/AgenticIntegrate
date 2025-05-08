import React from 'react';
import { Card, CardBody, Avatar, Chip } from "@nextui-org/react";
import { FiUser, FiCpu } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  const formattedTime = new Date(message.timestamp).toLocaleTimeString();

  // Custom renderer for code blocks
  const components = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
  };

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[85%] ${isUser ? 'order-2' : 'order-2'}`}>
        <Card 
          className={`
            ${isUser ? 'bg-primary-500 text-white' : 'glass-effect'} 
            border-none shadow-md
          `}
        >
          <CardBody className="py-3 px-4">
            <div className="flex items-center gap-2 mb-1">
              <Chip
                size="sm"
                variant="flat"
                color={isUser ? "primary" : "secondary"}
                className={isUser ? "text-white bg-primary-600" : ""}
              >
                {isUser ? 'You' : 'Assistant'}
              </Chip>
              <span className="text-xs opacity-70">{formattedTime}</span>
            </div>
            <div className="prose dark:prose-invert max-w-none">
              <ReactMarkdown components={components}>
                {message.content}
              </ReactMarkdown>
            </div>
          </CardBody>
        </Card>
      </div>
      <div className={`pt-2 ${isUser ? 'order-1 mr-2' : 'order-1 mr-2'}`}>
        <Avatar
          icon={isUser ? <FiUser /> : <FiCpu />}
          classNames={{
            base: isUser ? "bg-primary-200" : "bg-secondary-200",
            icon: isUser ? "text-primary-500" : "text-secondary-500",
          }}
        />
      </div>
    </div>
  );
};

export default ChatMessage;
