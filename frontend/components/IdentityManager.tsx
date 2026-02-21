'use client';

import { useState } from 'react';
import { Mail, Phone, MessageSquare, Plus, Trash2, Copy, ExternalLink } from 'lucide-react';

interface IdentityManagerProps {
  agentId: string | null;
}

interface EmailIdentity {
  id: string;
  address: string;
  domain: string;
  inboxCount: number;
  lastReceived: string;
  verified: boolean;
}

interface PhoneIdentity {
  id: string;
  number: string;
  region: string;
  smsCount: number;
  lastReceived: string;
  capabilities: string[];
}

export default function IdentityManager({ agentId }: IdentityManagerProps) {
  const [activeTab, setActiveTab] = useState<'email' | 'phone' | 'messages'>('email');

  // Mock data
  const emailIdentities: EmailIdentity[] = agentId
    ? [
        {
          id: 'email_1',
          address: 'support@agentid.io',
          domain: 'agentid.io',
          inboxCount: 47,
          lastReceived: '5 minutes ago',
          verified: true,
        },
      ]
    : [];

  const phoneIdentities: PhoneIdentity[] = agentId
    ? [
        {
          id: 'phone_1',
          number: '+1-555-0123',
          region: 'US',
          smsCount: 23,
          lastReceived: '12 minutes ago',
          capabilities: ['SMS', 'Voice'],
        },
      ]
    : [];

  if (!agentId) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <Mail className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No agent selected
          </h3>
          <p className="text-gray-500 dark:text-gray-400">
            Select an agent from the list to manage their identities
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Identity Manager</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Email addresses, phone numbers, and message routing
        </p>

        {/* Tabs */}
        <div className="flex space-x-4 mt-6 border-b border-gray-200 dark:border-gray-700">
          <button
            onClick={() => setActiveTab('email')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'email'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <Mail className="w-4 h-4 inline mr-2" />
            Email
          </button>
          <button
            onClick={() => setActiveTab('phone')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'phone'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <Phone className="w-4 h-4 inline mr-2" />
            Phone
          </button>
          <button
            onClick={() => setActiveTab('messages')}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'messages'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
            }`}
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Messages
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'email' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Email Addresses
              </h3>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                <Plus className="w-4 h-4" />
                <span>Add Email</span>
              </button>
            </div>

            <div className="space-y-4">
              {emailIdentities.map((email) => (
                <div
                  key={email.id}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-mono font-semibold text-gray-900 dark:text-white">
                          {email.address}
                        </h4>
                        {email.verified && (
                          <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded">
                            Verified
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Domain: {email.domain}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                        <Copy className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Inbox count:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {email.inboxCount}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Last received:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {email.lastReceived}
                      </span>
                    </div>
                  </div>

                  <button className="mt-3 flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700">
                    <span>View inbox</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'phone' && (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Phone Numbers
              </h3>
              <button className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                <Plus className="w-4 h-4" />
                <span>Add Phone</span>
              </button>
            </div>

            <div className="space-y-4">
              {phoneIdentities.map((phone) => (
                <div
                  key={phone.id}
                  className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="font-mono font-semibold text-gray-900 dark:text-white mb-1">
                        {phone.number}
                      </h4>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Region: {phone.region}
                      </p>
                    </div>
                    <div className="flex space-x-2">
                      <button className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                        <Copy className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-red-600">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-3">
                    {phone.capabilities.map((cap) => (
                      <span
                        key={cap}
                        className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 text-xs rounded"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">SMS count:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {phone.smsCount}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Last received:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {phone.lastReceived}
                      </span>
                    </div>
                  </div>

                  <button className="mt-3 flex items-center space-x-1 text-sm text-blue-600 hover:text-blue-700">
                    <span>View messages</span>
                    <ExternalLink className="w-3 h-3" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'messages' && (
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Recent Messages
            </h3>
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center">
              <MessageSquare className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-500 dark:text-gray-400">
                Message viewer coming soon
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
