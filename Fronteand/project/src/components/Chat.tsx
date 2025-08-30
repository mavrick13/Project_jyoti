import React, { useState, useRef, useEffect } from 'react';
import { useStore } from '../store/useStore';
import { Send, Hash, AtSign, Paperclip, Search } from 'lucide-react';

export function Chat() {
  const { user, messages, addMessage, farmers, tasks, addTask } = useStore();
  const [newMessage, setNewMessage] = useState('');
  const [showTagSuggestions, setShowTagSuggestions] = useState(false);
  const [showMentionSuggestions, setShowMentionSuggestions] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const commonTags = ['dispatch', 'installation', 'material', 'issue', 'urgent', 'completed'];
  const mockUsers = [
    { id: 'admin1', name: 'Admin User' },
    { id: 'employee1', name: 'Employee User' },
    { id: 'tech1', name: 'Tech Team 1' },
    { id: 'tech2', name: 'Tech Team 2' },
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMessage.trim() || !user) return;

    // Extract tags and mentions
    const tags = Array.from(newMessage.matchAll(/#(\w+)/g)).map(match => match[1]);
    const mentions = Array.from(newMessage.matchAll(/@(\w+)/g)).map(match => match[1]);

    // Check if this creates a task (contains @mention)
    let taskId: string | undefined;
    if (mentions.length > 0) {
      const taskTitle = `Task from chat: ${newMessage.substring(0, 50)}...`;
      const task = {
        title: taskTitle,
        description: newMessage,
        assignedTo: mentions[0], // Assign to first mentioned user
        assignedBy: user.id,
        status: 'pending' as const,
        priority: tags.includes('urgent') ? 'high' as const : 'medium' as const,
        tags: tags,
      };
      addTask(task);
      taskId = Date.now().toString(); // Mock task ID
    }

    addMessage({
      userId: user.id,
      userName: user.name,
      userAvatar: user.avatar,
      content: newMessage,
      tags,
      mentions,
      taskId,
    });

    setNewMessage('');
    setShowTagSuggestions(false);
    setShowMentionSuggestions(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setNewMessage(value);

    // Show tag suggestions when typing #
    const lastHashIndex = value.lastIndexOf('#');
    const lastSpaceAfterHash = value.indexOf(' ', lastHashIndex);
    if (lastHashIndex > -1 && (lastSpaceAfterHash === -1 || lastSpaceAfterHash < value.length - 1)) {
      setShowTagSuggestions(true);
      setShowMentionSuggestions(false);
    } else {
      setShowTagSuggestions(false);
    }

    // Show mention suggestions when typing @
    const lastAtIndex = value.lastIndexOf('@');
    const lastSpaceAfterAt = value.indexOf(' ', lastAtIndex);
    if (lastAtIndex > -1 && (lastSpaceAfterAt === -1 || lastSpaceAfterAt < value.length - 1)) {
      setShowMentionSuggestions(true);
      setShowTagSuggestions(false);
    } else if (!showTagSuggestions) {
      setShowMentionSuggestions(false);
    }
  };

  const insertTag = (tag: string) => {
    const lastHashIndex = newMessage.lastIndexOf('#');
    const beforeHash = newMessage.substring(0, lastHashIndex);
    const afterCursor = newMessage.substring(newMessage.length);
    setNewMessage(`${beforeHash}#${tag} ${afterCursor}`);
    setShowTagSuggestions(false);
  };

  const insertMention = (userId: string, userName: string) => {
    const lastAtIndex = newMessage.lastIndexOf('@');
    const beforeAt = newMessage.substring(0, lastAtIndex);
    const afterCursor = newMessage.substring(newMessage.length);
    setNewMessage(`${beforeAt}@${userId} ${afterCursor}`);
    setShowMentionSuggestions(false);
  };

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col bg-white rounded-xl shadow-sm">
      {/* Chat Header */}
      <div className="p-4 border-b bg-gray-50 rounded-t-xl">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Team Chat</h3>
            <p className="text-sm text-gray-500">Collaborate and assign tasks</p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
              <Search className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div key={message.id} className="flex space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
              <span className="text-sm font-medium text-blue-600">
                {message.userName.charAt(0)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-900">
                  {message.userName}
                </span>
                <span className="text-xs text-gray-500">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <p className="text-sm text-gray-700 mt-1">
                {message.content}
              </p>
              {(message.tags.length > 0 || message.mentions.length > 0 || message.taskId) && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {message.tags.map((tag) => (
                    <span key={tag} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                      <Hash className="w-3 h-3 mr-1" />
                      {tag}
                    </span>
                  ))}
                  {message.mentions.map((mention) => (
                    <span key={mention} className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                      <AtSign className="w-3 h-3 mr-1" />
                      {mention}
                    </span>
                  ))}
                  {message.taskId && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800">
                      Task Created
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t relative">
        {/* Tag Suggestions */}
        {showTagSuggestions && (
          <div className="absolute bottom-full left-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg mb-2 max-h-40 overflow-y-auto">
            {commonTags.map((tag) => (
              <button
                key={tag}
                onClick={() => insertTag(tag)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 transition-colors flex items-center space-x-2"
              >
                <Hash className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{tag}</span>
              </button>
            ))}
          </div>
        )}

        {/* Mention Suggestions */}
        {showMentionSuggestions && (
          <div className="absolute bottom-full left-4 right-4 bg-white border border-gray-200 rounded-lg shadow-lg mb-2 max-h-40 overflow-y-auto">
            {mockUsers.map((mockUser) => (
              <button
                key={mockUser.id}
                onClick={() => insertMention(mockUser.id, mockUser.name)}
                className="w-full text-left px-3 py-2 hover:bg-gray-50 transition-colors flex items-center space-x-2"
              >
                <AtSign className="w-4 h-4 text-gray-400" />
                <span className="text-sm">{mockUser.name}</span>
              </button>
            ))}
          </div>
        )}

        <form onSubmit={handleSendMessage} className="flex space-x-2">
          <div className="flex-1 relative">
            <textarea
              value={newMessage}
              onChange={handleInputChange}
              placeholder="Type a message... Use #tags and @mentions to organize and assign tasks"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              rows={2}
            />
          </div>
          <div className="flex flex-col space-y-2">
            <button
              type="button"
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <button
              type="submit"
              disabled={!newMessage.trim()}
              className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>

        <div className="mt-2 text-xs text-gray-500">
          Pro tip: Use #tags for categorization and @mentions to assign tasks to team members
        </div>
      </div>
    </div>
  );
}