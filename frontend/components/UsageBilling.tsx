'use client';

import { BarChart3, DollarSign, TrendingUp, Mail, Phone, Shield, CreditCard } from 'lucide-react';

export default function UsageBilling() {
  // Mock data
  const currentPeriod = {
    startDate: '2024-02-01',
    endDate: '2024-02-29',
    agents: 3,
    emailAddresses: 3,
    phoneNumbers: 2,
    emailsReceived: 1247,
    smsReceived: 456,
    vaultSecrets: 8,
    apiCalls: 12453,
  };

  const costs = {
    agents: 30, // $10/agent/month
    emails: 15.60, // based on volume
    sms: 22.80, // based on volume
    vault: 0, // included
    total: 68.40,
  };

  const paymentMethod = {
    type: 'card',
    last4: '4242',
    brand: 'Visa',
    expiresAt: '12/2025',
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">Usage & Billing</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Monitor usage and manage billing for your organization
        </p>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-6xl mx-auto space-y-6">
          {/* Current Bill Card */}
          <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-lg p-6 text-white">
            <div className="flex items-center justify-between mb-4">
              <div>
                <p className="text-blue-100 text-sm mb-1">Current billing period</p>
                <p className="text-white font-medium">
                  {currentPeriod.startDate} — {currentPeriod.endDate}
                </p>
              </div>
              <DollarSign className="w-12 h-12 text-blue-200" />
            </div>
            <div>
              <p className="text-4xl font-bold">${costs.total.toFixed(2)}</p>
              <p className="text-blue-100 text-sm mt-1">Estimated charges</p>
            </div>
          </div>

          {/* Usage Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-500 dark:text-gray-400 text-sm">Active Agents</span>
                <BarChart3 className="w-5 h-5 text-blue-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {currentPeriod.agents}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                $10/agent/month
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-500 dark:text-gray-400 text-sm">Email Volume</span>
                <Mail className="w-5 h-5 text-green-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {currentPeriod.emailsReceived.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                messages received
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-500 dark:text-gray-400 text-sm">SMS Volume</span>
                <Phone className="w-5 h-5 text-purple-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {currentPeriod.smsReceived.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                messages received
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-5">
              <div className="flex items-center justify-between mb-3">
                <span className="text-gray-500 dark:text-gray-400 text-sm">API Calls</span>
                <TrendingUp className="w-5 h-5 text-orange-600" />
              </div>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">
                {currentPeriod.apiCalls.toLocaleString()}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                this period
              </p>
            </div>
          </div>

          {/* Cost Breakdown */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="p-5 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Cost Breakdown
              </h3>
            </div>
            <div className="p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <BarChart3 className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Agents ({currentPeriod.agents} × $10)
                  </span>
                </div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  ${costs.agents.toFixed(2)}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Mail className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Email ({currentPeriod.emailsReceived} messages)
                  </span>
                </div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  ${costs.emails.toFixed(2)}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Phone className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    SMS ({currentPeriod.smsReceived} messages)
                  </span>
                </div>
                <span className="font-semibold text-gray-900 dark:text-white">
                  ${costs.sms.toFixed(2)}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <Shield className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-700 dark:text-gray-300">
                    Vault ({currentPeriod.vaultSecrets} secrets)
                  </span>
                </div>
                <span className="font-semibold text-gray-900 dark:text-white">Included</span>
              </div>

              <div className="pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
                <span className="font-semibold text-gray-900 dark:text-white">Total</span>
                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                  ${costs.total.toFixed(2)}
                </span>
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="p-5 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Payment Method
              </h3>
            </div>
            <div className="p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                    <CreditCard className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {paymentMethod.brand} •••• {paymentMethod.last4}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      Expires {paymentMethod.expiresAt}
                    </p>
                  </div>
                </div>
                <button className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 text-sm">
                  Update
                </button>
              </div>
            </div>
          </div>

          {/* Billing History */}
          <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg">
            <div className="p-5 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Billing History
              </h3>
            </div>
            <div className="p-5">
              <div className="space-y-3">
                {[
                  { date: '2024-01-01', amount: 52.30, status: 'Paid' },
                  { date: '2023-12-01', amount: 45.80, status: 'Paid' },
                  { date: '2023-11-01', amount: 38.20, status: 'Paid' },
                ].map((invoice, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  >
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">{invoice.date}</p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{invoice.status}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900 dark:text-white">
                        ${invoice.amount.toFixed(2)}
                      </p>
                      <button className="text-sm text-blue-600 hover:text-blue-700">
                        Download
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
