'use client';

import { useState } from 'react';
import Sidebar from '@/components/Sidebar';
import AgentList from '@/components/AgentList';
import IdentityManager from '@/components/IdentityManager';
import CredentialVault from '@/components/CredentialVault';
import ApiKeyManager from '@/components/ApiKeyManager';
import UsageBilling from '@/components/UsageBilling';

type View = 'agents' | 'identities' | 'vault' | 'api-keys' | 'usage';

export default function Dashboard() {
  const [currentView, setCurrentView] = useState<View>('agents');
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const renderView = () => {
    switch (currentView) {
      case 'agents':
        return <AgentList onSelectAgent={setSelectedAgent} selectedAgent={selectedAgent} />;
      case 'identities':
        return <IdentityManager agentId={selectedAgent} />;
      case 'vault':
        return <CredentialVault agentId={selectedAgent} />;
      case 'api-keys':
        return <ApiKeyManager />;
      case 'usage':
        return <UsageBilling />;
      default:
        return <AgentList onSelectAgent={setSelectedAgent} selectedAgent={selectedAgent} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      <main className="flex-1 overflow-y-auto">
        {renderView()}
      </main>
    </div>
  );
}
