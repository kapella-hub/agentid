'use client';

import { useState, useEffect, useCallback } from 'react';
import { Key, Plus, Copy, Trash2, Eye, EyeOff, CheckCircle, Check } from 'lucide-react';

interface ApiKey {
  id: string;
  name: string;
  key: string;
  prefix: string;
  scopes: string[];
  createdAt: string;
  lastUsed: string;
  expiresAt?: string;
  status: 'active' | 'revoked';
}

const AVAILABLE_SCOPES = ['agents:read', 'agents:write', 'identities:read', 'identities:write', 'vault:read', 'vault:write'];

export default function ApiKeyManager() {
  const [revealedKeys, setRevealedKeys] = useState<Set<string>>(new Set());
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [revokeConfirmId, setRevokeConfirmId] = useState<string | null>(null);

  // Form state
  const [keyName, setKeyName] = useState('');
  const [selectedScopes, setSelectedScopes] = useState<Set<string>>(new Set());
  const [expiration, setExpiration] = useState('never');
  const [formErrors, setFormErrors] = useState<{ name?: string; scopes?: string }>({});

  // Close modal on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowCreateModal(false);
        setRevokeConfirmId(null);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const resetForm = useCallback(() => {
    setKeyName('');
    setSelectedScopes(new Set());
    setExpiration('never');
    setFormErrors({});
  }, []);

  const handleCopy = useCallback(async (text: string, keyId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(keyId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Clipboard API not available
    }
  }, []);

  const handleRevoke = useCallback((keyId: string) => {
    // TODO: call api.apiKeys.revoke(keyId)
    setRevokeConfirmId(null);
  }, []);

  const toggleScope = useCallback((scope: string) => {
    setSelectedScopes((prev) => {
      const next = new Set(prev);
      if (next.has(scope)) next.delete(scope);
      else next.add(scope);
      return next;
    });
    setFormErrors((p) => ({ ...p, scopes: undefined }));
  }, []);

  const handleCreateKey = useCallback(() => {
    const errors: { name?: string; scopes?: string } = {};
    if (!keyName.trim()) errors.name = 'Key name is required';
    if (selectedScopes.size === 0) errors.scopes = 'Select at least one scope';
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    // TODO: call api.apiKeys.create({ name: keyName, scopes: [...selectedScopes] })
    setShowCreateModal(false);
    resetForm();
  }, [keyName, selectedScopes, resetForm]);

  // Mock data
  const apiKeys: ApiKey[] = [
    {
      id: 'key_1',
      name: 'Production Server',
      key: 'agid_prod_1234567890abcdefghijklmnopqrstuvwxyz',
      prefix: 'agid_prod_',
      scopes: ['agents:read', 'agents:write', 'identities:read', 'identities:write'],
      createdAt: '2024-02-15',
      lastUsed: '2 minutes ago',
      status: 'active',
    },
    {
      id: 'key_2',
      name: 'Development Environment',
      key: 'agid_dev_abcdefghijklmnopqrstuvwxyz1234567890',
      prefix: 'agid_dev_',
      scopes: ['agents:read', 'identities:read'],
      createdAt: '2024-02-10',
      lastUsed: '1 hour ago',
      expiresAt: '2024-08-10',
      status: 'active',
    },
    {
      id: 'key_3',
      name: 'Old CI/CD Key',
      key: 'agid_ci_xyz123456789abcdefghijklmnopqrstuvw',
      prefix: 'agid_ci_',
      scopes: ['agents:read'],
      createdAt: '2024-01-15',
      lastUsed: '10 days ago',
      status: 'revoked',
    },
  ];

  const toggleReveal = (keyId: string) => {
    const newRevealed = new Set(revealedKeys);
    if (newRevealed.has(keyId)) {
      newRevealed.delete(keyId);
    } else {
      newRevealed.add(keyId);
    }
    setRevealedKeys(newRevealed);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">API Keys</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Manage your organization&apos;s API keys
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <Plus className="w-4 h-4" />
            <span>Create Key</span>
          </button>
        </div>

        {/* Info Banner */}
        <div className="mt-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <Key className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-blue-800 dark:text-blue-200">
                API keys provide programmatic access to AgentID. Keep them secure and never commit
                them to version control. Use environment variables instead.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* API Keys List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-4">
          {apiKeys.map((apiKey) => {
            const isRevealed = revealedKeys.has(apiKey.id);
            const isRevoked = apiKey.status === 'revoked';

            return (
              <div
                key={apiKey.id}
                className={`bg-white dark:bg-gray-800 border rounded-lg p-5 ${
                  isRevoked
                    ? 'border-red-200 dark:border-red-800 opacity-75'
                    : 'border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="font-semibold text-gray-900 dark:text-white">
                        {apiKey.name}
                      </h4>
                      {isRevoked ? (
                        <span className="px-2 py-0.5 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-xs rounded">
                          Revoked
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded flex items-center space-x-1">
                          <CheckCircle className="w-3 h-3" />
                          <span>Active</span>
                        </span>
                      )}
                    </div>

                    {/* API Key Display */}
                    <div className="flex items-center space-x-2 mb-4">
                      <code className="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-700 rounded font-mono text-sm text-gray-900 dark:text-white break-all">
                        {isRevealed ? apiKey.key : `${apiKey.prefix}\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022`}
                      </code>
                      <button
                        onClick={() => toggleReveal(apiKey.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        aria-label={isRevealed ? 'Hide API key' : 'Reveal API key'}
                        title={isRevealed ? 'Hide' : 'Reveal'}
                      >
                        {isRevealed ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleCopy(apiKey.key, apiKey.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        aria-label="Copy API key"
                        title="Copy to clipboard"
                      >
                        {copiedId === apiKey.id ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>

                    {/* Scopes */}
                    <div className="mb-3">
                      <span className="text-xs font-medium text-gray-500 dark:text-gray-400 mr-2">
                        Scopes:
                      </span>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {apiKey.scopes.map((scope) => (
                          <span
                            key={scope}
                            className="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded font-mono"
                          >
                            {scope}
                          </span>
                        ))}
                      </div>
                    </div>

                    {/* Metadata */}
                    <div className="grid grid-cols-3 gap-4 text-xs text-gray-500 dark:text-gray-400">
                      <div>
                        <span>Created:</span>
                        <span className="ml-1 text-gray-900 dark:text-white">{apiKey.createdAt}</span>
                      </div>
                      <div>
                        <span>Last used:</span>
                        <span className="ml-1 text-gray-900 dark:text-white">{apiKey.lastUsed}</span>
                      </div>
                      {apiKey.expiresAt && (
                        <div>
                          <span>Expires:</span>
                          <span className="ml-1 text-gray-900 dark:text-white">{apiKey.expiresAt}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {!isRevoked && (
                    revokeConfirmId === apiKey.id ? (
                      <div className="flex flex-col items-end space-y-1">
                        <button
                          onClick={() => handleRevoke(apiKey.id)}
                          className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                        >
                          Confirm Revoke
                        </button>
                        <button
                          onClick={() => setRevokeConfirmId(null)}
                          className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded text-gray-600 dark:text-gray-400"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setRevokeConfirmId(apiKey.id)}
                        className="p-2 text-gray-400 hover:text-red-600"
                        aria-label="Revoke API key"
                        title="Revoke key"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={(e) => { if (e.target === e.currentTarget) { setShowCreateModal(false); resetForm(); } }}
          role="dialog"
          aria-modal="true"
          aria-labelledby="create-key-title"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h3 id="create-key-title" className="text-xl font-bold text-gray-900 dark:text-white mb-4">Create API Key</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="key-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Key Name
                </label>
                <input
                  id="key-name"
                  type="text"
                  placeholder="e.g., Production Server"
                  value={keyName}
                  onChange={(e) => { setKeyName(e.target.value); setFormErrors((p) => ({ ...p, name: undefined })); }}
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${formErrors.name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
                />
                {formErrors.name && <p className="text-sm text-red-500 mt-1">{formErrors.name}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Scopes
                </label>
                <div className="space-y-2">
                  {AVAILABLE_SCOPES.map((scope) => (
                    <label key={scope} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedScopes.has(scope)}
                        onChange={() => toggleScope(scope)}
                        className="rounded border-gray-300 dark:border-gray-600"
                      />
                      <span className="text-sm text-gray-700 dark:text-gray-300 font-mono">
                        {scope}
                      </span>
                    </label>
                  ))}
                </div>
                {formErrors.scopes && <p className="text-sm text-red-500 mt-1">{formErrors.scopes}</p>}
              </div>

              <div>
                <label htmlFor="key-expiration" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Expiration (optional)
                </label>
                <select
                  id="key-expiration"
                  value={expiration}
                  onChange={(e) => setExpiration(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="never">Never</option>
                  <option value="30d">30 days</option>
                  <option value="90d">90 days</option>
                  <option value="1y">1 year</option>
                </select>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => { setShowCreateModal(false); resetForm(); }}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateKey}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create Key
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
