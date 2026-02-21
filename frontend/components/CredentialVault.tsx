'use client';

import { useState, useEffect, useCallback } from 'react';
import { Shield, Plus, Eye, EyeOff, Copy, Trash2, Key, Lock, Check } from 'lucide-react';

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
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  // Form state
  const [secretName, setSecretName] = useState('');
  const [secretType, setSecretType] = useState<Secret['type']>('api-key');
  const [secretValue, setSecretValue] = useState('');
  const [formErrors, setFormErrors] = useState<{ name?: string; value?: string }>({});

  // Close modals on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setShowCreateModal(false);
        setDeleteConfirmId(null);
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const resetForm = useCallback(() => {
    setSecretName('');
    setSecretType('api-key');
    setSecretValue('');
    setFormErrors({});
  }, []);

  const handleCopy = useCallback(async (text: string, secretId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedId(secretId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch {
      // Clipboard API not available
    }
  }, []);

  const handleDelete = useCallback((secretId: string) => {
    // TODO: call api.vault.delete(secretId)
    setDeleteConfirmId(null);
  }, []);

  const handleCreateSecret = useCallback(() => {
    const errors: { name?: string; value?: string } = {};
    if (!secretName.trim()) errors.name = 'Name is required';
    if (!secretValue.trim()) errors.value = 'Value is required';
    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }
    // TODO: call api.vault.create({ name: secretName, value: secretValue, type: secretType, agent_id: agentId })
    setShowCreateModal(false);
    resetForm();
  }, [secretName, secretValue, secretType, agentId, resetForm]);

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
                        {isRevealed ? 'xxxx_test_EXAMPLE_KEY_NOT_REAL_12345' : '\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022\u2022'}
                      </code>
                      <button
                        onClick={() => toggleReveal(secret.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        aria-label={isRevealed ? 'Hide secret' : 'Reveal secret'}
                        title={isRevealed ? 'Hide' : 'Reveal'}
                      >
                        {isRevealed ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleCopy('xxxx_test_EXAMPLE_KEY_NOT_REAL_12345', secret.id)}
                        className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                        aria-label="Copy to clipboard"
                        title="Copy to clipboard"
                      >
                        {copiedId === secret.id ? <Check className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
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

                  {deleteConfirmId === secret.id ? (
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={() => handleDelete(secret.id)}
                        className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={() => setDeleteConfirmId(null)}
                        className="px-2 py-1 text-xs border border-gray-300 dark:border-gray-600 rounded text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => setDeleteConfirmId(secret.id)}
                      className="p-2 text-gray-400 hover:text-red-600"
                      aria-label="Delete secret"
                      title="Delete"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
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
          aria-labelledby="add-secret-title"
        >
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
            <h3 id="add-secret-title" className="text-xl font-bold text-gray-900 dark:text-white mb-4">Add Secret</h3>
            <div className="space-y-4">
              <div>
                <label htmlFor="secret-name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Name
                </label>
                <input
                  id="secret-name"
                  type="text"
                  placeholder="e.g., OpenAI API Key"
                  value={secretName}
                  onChange={(e) => { setSecretName(e.target.value); setFormErrors((p) => ({ ...p, name: undefined })); }}
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${formErrors.name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
                />
                {formErrors.name && <p className="text-sm text-red-500 mt-1">{formErrors.name}</p>}
              </div>
              <div>
                <label htmlFor="secret-type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Type
                </label>
                <select
                  id="secret-type"
                  value={secretType}
                  onChange={(e) => setSecretType(e.target.value as Secret['type'])}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="api-key">API Key</option>
                  <option value="password">Password</option>
                  <option value="2fa-seed">2FA Seed</option>
                  <option value="oauth-token">OAuth Token</option>
                </select>
              </div>
              <div>
                <label htmlFor="secret-value" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Value
                </label>
                <input
                  id="secret-value"
                  type="password"
                  placeholder="Enter secret value"
                  value={secretValue}
                  onChange={(e) => { setSecretValue(e.target.value); setFormErrors((p) => ({ ...p, value: undefined })); }}
                  className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${formErrors.value ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'}`}
                />
                {formErrors.value && <p className="text-sm text-red-500 mt-1">{formErrors.value}</p>}
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
                onClick={handleCreateSecret}
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
