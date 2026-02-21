'use client';

import { useState, useEffect, useCallback } from 'react';
import { Plus, Search, Bot, Mail, Phone, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  email: string | null;
  phone: string | null;
  createdAt: string;
  lastActive: string;
}

interface AgentListProps {
  onSelectAgent: (agentId: string | null) => void;
  selectedAgent: string | null;
}

export default function AgentList({ onSelectAgent, selectedAgent }: AgentListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newAgentName, setNewAgentName] = useState('');
  const [nameError, setNameError] = useState('');

  // Close modal on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showCreateModal) {
        setShowCreateModal(false);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showCreateModal]);

  const handleCreate = useCallback(() => {
    const trimmed = newAgentName.trim();
    if (!trimmed) {
      setNameError('Agent name is required');
      return;
    }
    if (trimmed.length < 2) {
      setNameError('Name must be at least 2 characters');
      return;
    }
    // TODO: call api.agents.create({ name: trimmed })
    setShowCreateModal(false);
    setNewAgentName('');
    setNameError('');
  }, [newAgentName]);

  // Mock data - would come from API
  const agents: Agent[] = [
    {
      id: 'agt_1',
      name: 'customer-support-bot',
      status: 'active',
      email: 'support@agentid.io',
      phone: '+1-555-0123',
      createdAt: '2024-02-15',
      lastActive: '2 minutes ago',
    },
    {
      id: 'agt_2',
      name: 'sales-assistant',
      status: 'active',
      email: 'sales@agentid.io',
      phone: null,
      createdAt: '2024-02-14',
      lastActive: '15 minutes ago',
    },
    {
      id: 'agt_3',
      name: 'data-processor',
      status: 'inactive',
      email: null,
      phone: null,
      createdAt: '2024-02-10',
      lastActive: '3 days ago',
    },
  ];

  const filteredAgents = agents.filter((agent) =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'inactive':
        return <AlertCircle className="w-4 h-4 text-gray-400" />;
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />;
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Agents</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Manage your AI agent identities
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Agent</span>
          </button>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search agents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Search agents"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Agent List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="grid gap-4">
          {filteredAgents.map((agent) => (
            <div
              key={agent.id}
              onClick={() => onSelectAgent(agent.id === selectedAgent ? null : agent.id)}
              className={`bg-white dark:bg-gray-800 border rounded-lg p-5 cursor-pointer transition-all ${
                selectedAgent === agent.id
                  ? 'border-blue-500 ring-2 ring-blue-500 ring-opacity-50'
                  : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <Bot className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 dark:text-white">{agent.name}</h3>
                    <p className="text-xs text-gray-500 dark:text-gray-400">ID: {agent.id}</p>
                  </div>
                </div>
                {getStatusIcon(agent.status)}
              </div>

              <div className="space-y-2">
                <div className="flex items-center space-x-2 text-sm">
                  <Mail className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600 dark:text-gray-300">
                    {agent.email || 'No email configured'}
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-sm">
                  <Phone className="w-4 h-4 text-gray-400" />
                  <span className="text-gray-600 dark:text-gray-300">
                    {agent.phone || 'No phone configured'}
                  </span>
                </div>
              </div>

              <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                <span>Created {agent.createdAt}</span>
                <span>Active {agent.lastActive}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => { if (e.target === e.currentTarget) setShowCreateModal(false); }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="create-agent-title"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h3 id="create-agent-title" className="text-xl font-bold text-gray-900 dark:text-white mb-4">Create New Agent</h3>
            <div>
              <label htmlFor="agent-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Agent Name
              </label>
              <input
                id="agent-name"
                type="text"
                placeholder="e.g., customer-support-bot"
                value={newAgentName}
                onChange={(e) => { setNewAgentName(e.target.value); setNameError(''); }}
                onKeyDown={(e) => { if (e.key === 'Enter') handleCreate(); }}
                className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white mb-1 ${
                  nameError ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                }`}
              />
              {nameError && <p className="text-sm text-red-500 mb-3">{nameError}</p>}
            </div>
            <div className="flex space-x-3 mt-4">
              <button
                onClick={() => { setShowCreateModal(false); setNewAgentName(''); setNameError(''); }}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCreate}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
