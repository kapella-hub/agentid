/**
 * AgentID API Client
 * 
 * Provides typed interfaces for interacting with the AgentID backend API.
 * Configuration is read from environment variables.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';

interface ApiRequestOptions extends RequestInit {
  params?: Record<string, string | undefined>;
  timeoutMs?: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
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
    const { params, headers, timeoutMs = 30000, ...fetchOptions } = options;

    // Build URL with query params (filter out undefined values)
    let url = `${this.baseUrl}${endpoint}`;
    if (params) {
      const filtered: Record<string, string> = {};
      for (const [k, v] of Object.entries(params)) {
        if (v !== undefined) filtered[k] = v;
      }
      if (Object.keys(filtered).length > 0) {
        url += `?${new URLSearchParams(filtered).toString()}`;
      }
    }

    // Prepare headers
    const requestHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(headers as Record<string, string>),
    };

    if (this.apiKey) {
      requestHeaders['Authorization'] = `Bearer ${this.apiKey}`;
    }

    // Set up timeout via AbortController
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers: requestHeaders,
        signal: controller.signal,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({
          message: response.statusText,
        }));
        throw new ApiError(
          error.message || error.error?.message || `API error: ${response.status}`,
          response.status,
          error.error?.code,
        );
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return undefined as T;
      }

      return response.json();
    } catch (err) {
      if (err instanceof ApiError) throw err;
      if (err instanceof DOMException && err.name === 'AbortError') {
        throw new ApiError('Request timed out', 0, 'timeout');
      }
      throw new ApiError(
        err instanceof Error ? err.message : 'Network error',
        0,
        'network_error',
      );
    } finally {
      clearTimeout(timeoutId);
    }
  }

  // Agent endpoints
  agents = {
    list: () => this.request('/agents'),
    get: (id: string) => this.request(`/agents/${id}`),
    create: (data: { name: string; description?: string }) =>
      this.request('/agents', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: Partial<{ name: string; description: string; status: string }>) =>
      this.request(`/agents/${id}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      this.request(`/agents/${id}`, { method: 'DELETE' }),
  };

  // Identity endpoints
  identities = {
    email: {
      list: (agentId: string) =>
        this.request(`/agents/${agentId}/email`),
      create: (agentId: string, data: { domain?: string }) =>
        this.request(`/agents/${agentId}/email`, {
          method: 'POST',
          body: JSON.stringify(data),
        }),
      delete: (agentId: string, emailId: string) =>
        this.request(`/agents/${agentId}/email/${emailId}`, { method: 'DELETE' }),
    },
    phone: {
      list: (agentId: string) =>
        this.request(`/agents/${agentId}/phone`),
      create: (agentId: string, data: { region: string }) =>
        this.request(`/agents/${agentId}/phone`, {
          method: 'POST',
          body: JSON.stringify(data),
        }),
      delete: (agentId: string, phoneId: string) =>
        this.request(`/agents/${agentId}/phone/${phoneId}`, { method: 'DELETE' }),
    },
  };

  // Message endpoints
  messages = {
    email: (params?: { agent_id?: string; direction?: string; limit?: number }) =>
      this.request('/messages', { params: { channel: 'email', ...params } as Record<string, string | undefined> }),
    sms: (params?: { agent_id?: string; direction?: string; limit?: number }) =>
      this.request('/messages', { params: { channel: 'sms', ...params } as Record<string, string | undefined> }),
    get: (id: string) => this.request(`/messages/${id}`),
    send: (data: { agent_id: string; to: string; channel: 'email' | 'sms'; body: string; subject?: string }) =>
      this.request('/messages/send', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
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
    update: (secretId: string, data: { value: string }) =>
      this.request(`/secrets/${secretId}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
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

  // Webhook endpoints
  webhooks = {
    list: () => this.request('/webhooks'),
    create: (data: { url: string; events: string[]; agent_id?: string }) =>
      this.request('/webhooks', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    delete: (webhookId: string) =>
      this.request(`/webhooks/${webhookId}`, { method: 'DELETE' }),
  };

  // Audit log endpoints
  audit = {
    list: (params?: { action?: string; resource_type?: string; limit?: number }) =>
      this.request('/audit', { params: params as Record<string, string | undefined> }),
  };

  // Usage & billing
  // NOTE: These billing endpoints are stubs — the backend does not implement
  // billing routes. These are kept as placeholders for future integration.
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
  description?: string;
  org_id: string;
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
  agent_id?: string;
  org_id: string;
  version: number;
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
