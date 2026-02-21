'use client';

import { useState } from 'react';
import { Shield, Plus, Eye, EyeOff, Copy, Trash2, Key, Lock } from 'lucide-react';

interface CredentialVaultProps {
  agentId: string | null;
}

interface Secret {
  id: string;
  name: string;
  type: 'api-key' | 'password' | '2fa-seed' | 'oauth-token';
  createdAt: string;
  lastUsed: string;
  expiresAt?: string;
}

export default function CredentialVault({ agentId }: CredentialVaultProps) {
  const [revealedSecrets, setRevealedSecrets] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);

  // Mock data
  const secrets: Secret[] = agentId
    ? [
        {
          id: 'sec_1',
          name: 'OpenAI API Key',
          type: 'api-key',
          createdAt: '2024-02-15',
          lastUsed: '2 hours ago',
          expiresAt: '2024-08-15',
        },
        {
          id: 'sec_2',
          name: 'Stripe Secret Key',
          type: 'api-key',
          createdAt: '2024-02-10',
          lastUsed: '1 day ago',
        },
        {
          id: 'sec_3',
          name: 'Database Password',
          type: 'password',
          createdAt: '2024-02-05',
          lastUsed: '3 hours ago',
        },
      ]
    : [];

  const toggleReveal = (secretId: string) => {
    const newRevealed = new Set(revealedSecrets);
    if (newRevealed.has(secretId)) {
      newRevealed.delete(secretId);
    } else {
      newRevealed.add(secretId);
    }
    setRevealedSecrets(newRevealed);
  };

  const getTypeColor = (type: Secret['type']) => {
    switch (type) {
      case 'api-key':
        return 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400';
      case 'password':
        return 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400';
      case '2fa-seed':
        return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400';
      case 'oauth-token':
        return 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-400';
    }
  };

  if (!agentId) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Shield className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No agent selected
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Select an agent to view and manage their credentials
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Credential Vault</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Encrypted secrets and API keys
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            <span>Add Secret</span>
          </button>
        </div>

        {/* Security Notice */}
        <div className="mt-4 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Lock className="w-5 h-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-amber-800 dark:text-amber-200">
                <strong>Encrypted at rest:</strong> All secrets are encrypted using envelope encryption
                with KMS. Requires MFA for reveal in production.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Secrets List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          {secrets.map((secret) => {
            const isRevealed = revealedSecrets.has(secret.id);
            return (
              <div
                key={secret.id}
                className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <Key className="w-4 h-4 text-gray-400" />
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        {secret.name}
                      </h4>
                      <span className={`px-2 py-0.5 text-xs rounded ${getTypeColor(secret.type)}`}>
                        {secret.type}
                      </span>
                    </div>

                    {/* Secret Value */}
                    <div className="flex items-center space-x-2 mb-3">
                      <code className="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded font-mono text-sm text-gray-900 dark:text-white">
                        {isRevealed ? 'xxxx_test_EXAMPLE_KEY_NOT_REAL_12345' : '••••••••••••••••••••••••••••'}
                      </code>
                      <button
                        onClick={() => toggleReveal(secret.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        {isRevealed ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                        <Copy className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-3 gap-4 text-xs text-gray-500 dark:text-gray-400">
                      <div>
                        <span>Created:</span>
                        <span className="ml-1 text-gray-900 dark:text-white">{secret.createdAt}</span>
                      </div>
                      <div>
                        <span>Last used:</span>
                        <span className="ml-1 text-gray-900 dark:text-white">{secret.lastUsed}</span>
                      </div>
                      {secret.expiresAt && (
                        <div>
                          <span>Expires:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{secret.expiresAt}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <button className="p-2 text-gray-400 hover:text-red-600">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Add Secret</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  placeholder="e.g., OpenAI API Key"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Type
                </label>
                <select className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option>API Key</option>
                  <option>Password</option>
                  <option>2FA Seed</option>
                  <option>OAuth Token</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Value
                </label>
                <input
                  type="password"
                  placeholder="Enter secret value"
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Add Secret
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
