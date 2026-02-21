/**
 * AgentID API Client
 * 
 * Provides typed interfaces for interacting with the AgentID backend API.
 * Configuration is read from environment variables.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string>;
}

/**
 * Base API client with authentication and error handling
 */
class ApiClient {
  private baseUrl: string;
  private apiKey: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = `${baseUrl}/${API_VERSION}`;
  }

  /**
   * Set the API key for authenticated requests
   */
  setApiKey(key: string) {
    this.apiKey = key;
  }

  /**
   * Make an authenticated API request
   */
  private async request<T>(
    endpoint: string,
    options: ApiRequestOptions = {}
  ): Promise<T> {
    const { params, headers, ...fetchOptions } = options;

    // Build URL with query params
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const searchParams = new URLSearchParams(params);
      url += `?${searchParams.toString()}`;
    }

    // Prepare headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(headers as Record<string, string>),
    };

    if (this.apiKey) {
      requestHeaders['Authorization'] = `Bearer ${this.apiKey}`;
    }

    // Make request
    const response = await fetch(url, {
      ...fetchOptions,
      headers: requestHeaders,
    });

    // Handle errors
    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.message || `API error: ${response.status}`);
    }

    return response.json();
  }

  // Agent endpoints
  agents = {
    list: () => this.request('/agents'),
    get: (id: string) => this.request(`/agents/${id}`),
    create: (data: { name: string }) =>
      this.request('/agents', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      this.request(`/agents/${id}`, { method: 'DELETE' }),
  };

  // Identity endpoints
  identities = {
    email: {
      list: (agentId: string) =>
        this.request(`/agents/${agentId}/email`, { params: { agent_id: agentId } }),
      create: (agentId: string, data: { domain?: string }) =>
        this.request(`/agents/${agentId}/email`, {
          method: 'POST',
          body: JSON.stringify(data),
        }),
      delete: (emailId: string) =>
        this.request(`/identities/email/${emailId}`, { method: 'DELETE' }),
    },
    phone: {
      list: (agentId: string) =>
        this.request(`/agents/${agentId}/phone`, { params: { agent_id: agentId } }),
      create: (agentId: string, data: { region: string }) =>
        this.request(`/agents/${agentId}/phone`, {
          method: 'POST',
          body: JSON.stringify(data),
        }),
      delete: (phoneId: string) =>
        this.request(`/identities/phone/${phoneId}`, { method: 'DELETE' }),
    },
  };

  // Message endpoints
  messages = {
    email: (params: { agent_id?: string; limit?: number }) =>
      this.request('/messages/email', { params: params as any }),
    sms: (params: { agent_id?: string; limit?: number }) =>
      this.request('/messages/sms', { params: params as any }),
  };

  // Vault endpoints
  vault = {
    list: (agentId?: string) =>
      this.request('/secrets', { params: agentId ? { agent_id: agentId } : undefined }),
    get: (secretId: string) => this.request(`/secrets/${secretId}`),
    create: (data: { name: string; value: string; type: string; agent_id?: string }) =>
      this.request('/secrets', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    rotate: (secretId: string) =>
      this.request(`/secrets/${secretId}/rotate`, { method: 'POST' }),
    delete: (secretId: string) =>
      this.request(`/secrets/${secretId}`, { method: 'DELETE' }),
  };

  // API Key management
  apiKeys = {
    list: () => this.request('/api-keys'),
    create: (data: { name: string; scopes: string[]; expires_at?: string }) =>
      this.request('/api-keys', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    revoke: (keyId: string) =>
      this.request(`/api-keys/${keyId}`, { method: 'DELETE' }),
  };

  // Usage & billing
  billing = {
    usage: (params?: { start_date?: string; end_date?: string }) =>
      this.request('/billing/usage', { params: params as any }),
    invoices: () => this.request('/billing/invoices'),
    paymentMethod: () => this.request('/billing/payment-method'),
    updatePaymentMethod: (data: { token: string }) =>
      this.request('/billing/payment-method', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
  };
}

// Export singleton instance
export const api = new ApiClient();

// Export types for convenience
export type Agent = {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  created_at: string;
  last_active: string;
};

export type EmailIdentity = {
  id: string;
  agent_id: string;
  address: string;
  domain: string;
  verified: boolean;
  created_at: string;
};

export type PhoneIdentity = {
  id: string;
  agent_id: string;
  number: string;
  region: string;
  capabilities: string[];
  created_at: string;
};

export type Secret = {
  id: string;
  name: string;
  type: 'api-key' | 'password' | '2fa-seed' | 'oauth-token';
  created_at: string;
  expires_at?: string;
};

export type ApiKey = {
  id: string;
  name: string;
  key: string;
  prefix: string;
  scopes: string[];
  created_at: string;
  expires_at?: string;
  status: 'active' | 'revoked';
};
