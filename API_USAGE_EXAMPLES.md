# SESPCLSwitch API - Usage Examples

## Overview
This document provides practical examples for integrating with the SESPCLSwitch API using various programming languages and tools.

## Base URL
```
http://167.172.135.7:5000
```

---

## 1. PowerShell Examples

### Health Check
```powershell
Invoke-RestMethod -Uri "http://167.172.135.7:5000/health" -Method GET
```

### Make a Voice Call
```powershell
$body = @{
    ToNumber = "+1234567890"
    FromNumber = "12156"
    Text = "Hello from SESPCLSwitch!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://167.172.135.7:5000/voice/call" -Method POST -ContentType "application/json" -Body $body
Write-Output "Call ID: $($response.call_id)"
Write-Output "Status: $($response.status)"
```

### Check Call Status
```powershell
$callId = "18885f34-d743-4ca1-96a8-55d340bd3937"
Invoke-RestMethod -Uri "http://167.172.135.7:5000/voice/status/$callId" -Method GET
```

### Bulk Voice Calls
```powershell
$bulkBody = @{
    calls = @(
        @{
            ToNumber = "+1234567890"
            FromNumber = "12156"
            Text = "First call message"
        },
        @{
            ToNumber = "+0987654321"
            FromNumber = "12156"
            Text = "Second call message"
        }
    )
} | ConvertTo-Json -Depth 3

Invoke-RestMethod -Uri "http://167.172.135.7:5000/voice/bulk" -Method POST -ContentType "application/json" -Body $bulkBody
```

---

## 2. cURL Examples

### Health Check
```bash
curl http://167.172.135.7:5000/health
```

### Make a Voice Call
```bash
curl -X POST http://167.172.135.7:5000/voice/call \
  -H "Content-Type: application/json" \
  -d '{
    "ToNumber": "+1234567890",
    "FromNumber": "12156",
    "Text": "Hello from SESPCLSwitch!"
  }'
```

### Check Call Status
```bash
curl http://167.172.135.7:5000/voice/status/18885f34-d743-4ca1-96a8-55d340bd3937
```

### System Metrics
```bash
curl http://167.172.135.7:5000/api/metrics
```

### Bulk Voice Calls
```bash
curl -X POST http://167.172.135.7:5000/voice/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "calls": [
      {
        "ToNumber": "+1234567890",
        "FromNumber": "12156",
        "Text": "First call message"
      },
      {
        "ToNumber": "+0987654321",
        "FromNumber": "12156",
        "Text": "Second call message"
      }
    ]
  }'
```

---

## 3. Python Examples

### Installation
```bash
pip install requests
```

### Basic Usage
```python
import requests
import json
import time

# Base URL
BASE_URL = "http://167.172.135.7:5000"

def check_health():
    """Check API health status"""
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

def make_voice_call(to_number, from_number, text):
    """Make a voice call"""
    payload = {
        "ToNumber": to_number,
        "FromNumber": from_number,
        "Text": text
    }
    
    response = requests.post(
        f"{BASE_URL}/voice/call",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 202:
        return response.json()
    else:
        raise Exception(f"Call failed: {response.text}")

def check_call_status(call_id):
    """Check the status of a call"""
    response = requests.get(f"{BASE_URL}/voice/status/{call_id}")
    return response.json()

def get_system_metrics():
    """Get system performance metrics"""
    response = requests.get(f"{BASE_URL}/api/metrics")
    return response.json()

def make_bulk_calls(calls_list):
    """Make multiple calls in bulk"""
    payload = {"calls": calls_list}
    
    response = requests.post(
        f"{BASE_URL}/voice/bulk",
        headers={"Content-Type": "application/json"},
        json=payload
    )
    
    if response.status_code == 202:
        return response.json()
    else:
        raise Exception(f"Bulk call failed: {response.text}")

# Example usage
if __name__ == "__main__":
    # Check health
    health = check_health()
    print(f"API Status: {health['status']}")
    
    # Make a call
    call_response = make_voice_call(
        to_number="+1234567890",
        from_number="12156",
        text="Hello from Python SESPCLSwitch integration!"
    )
    
    call_id = call_response["call_id"]
    print(f"Call initiated: {call_id}")
    
    # Wait and check status
    time.sleep(5)
    status = check_call_status(call_id)
    print(f"Call status: {status['status']}")
    
    # Get metrics
    metrics = get_system_metrics()
    print(f"Total calls: {metrics['calls']['total']}")
```

---

## 4. JavaScript/Node.js Examples

### Installation
```bash
npm install axios
```

### Basic Usage
```javascript
const axios = require('axios');

const BASE_URL = 'http://167.172.135.7:5000';

class SESPCLSwitchClient {
    constructor(baseUrl = BASE_URL) {
        this.baseUrl = baseUrl;
        this.client = axios.create({
            baseURL: baseUrl,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    async checkHealth() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            throw new Error(`Health check failed: ${error.message}`);
        }
    }

    async makeVoiceCall(toNumber, fromNumber, text) {
        try {
            const payload = {
                ToNumber: toNumber,
                FromNumber: fromNumber,
                Text: text
            };

            const response = await this.client.post('/voice/call', payload);
            return response.data;
        } catch (error) {
            throw new Error(`Voice call failed: ${error.message}`);
        }
    }

    async checkCallStatus(callId) {
        try {
            const response = await this.client.get(`/voice/status/${callId}`);
            return response.data;
        } catch (error) {
            throw new Error(`Status check failed: ${error.message}`);
        }
    }

    async getSystemMetrics() {
        try {
            const response = await this.client.get('/api/metrics');
            return response.data;
        } catch (error) {
            throw new Error(`Metrics fetch failed: ${error.message}`);
        }
    }

    async makeBulkCalls(callsList) {
        try {
            const payload = { calls: callsList };
            const response = await this.client.post('/voice/bulk', payload);
            return response.data;
        } catch (error) {
            throw new Error(`Bulk call failed: ${error.message}`);
        }
    }
}

// Example usage
(async () => {
    const client = new SESPCLSwitchClient();

    try {
        // Check health
        const health = await client.checkHealth();
        console.log(`API Status: ${health.status}`);

        // Make a call
        const callResponse = await client.makeVoiceCall(
            '+1234567890',
            '12156',
            'Hello from Node.js SESPCLSwitch integration!'
        );

        console.log(`Call initiated: ${callResponse.call_id}`);

        // Wait and check status
        setTimeout(async () => {
            const status = await client.checkCallStatus(callResponse.call_id);
            console.log(`Call status: ${status.status}`);
        }, 5000);

        // Get metrics
        const metrics = await client.getSystemMetrics();
        console.log(`Total calls: ${metrics.calls.total}`);

    } catch (error) {
        console.error('Error:', error.message);
    }
})();
```

---

## 5. C# Examples

### Installation
```bash
dotnet add package Newtonsoft.Json
```

### Basic Usage
```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class SESPCLSwitchClient
{
    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public SESPCLSwitchClient(string baseUrl = "http://167.172.135.7:5000")
    {
        _baseUrl = baseUrl;
        _httpClient = new HttpClient();
        _httpClient.DefaultRequestHeaders.Add("Content-Type", "application/json");
    }

    public async Task<dynamic> CheckHealthAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/health");
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(content);
    }

    public async Task<dynamic> MakeVoiceCallAsync(string toNumber, string fromNumber, string text)
    {
        var payload = new
        {
            ToNumber = toNumber,
            FromNumber = fromNumber,
            Text = text
        };

        var json = JsonConvert.SerializeObject(payload);
        var content = new StringContent(json, Encoding.UTF8, "application/json");

        var response = await _httpClient.PostAsync($"{_baseUrl}/voice/call", content);
        var responseContent = await response.Content.ReadAsStringAsync();
        
        if (response.IsSuccessStatusCode)
        {
            return JsonConvert.DeserializeObject(responseContent);
        }
        
        throw new Exception($"Call failed: {responseContent}");
    }

    public async Task<dynamic> CheckCallStatusAsync(string callId)
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/voice/status/{callId}");
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(content);
    }

    public async Task<dynamic> GetSystemMetricsAsync()
    {
        var response = await _httpClient.GetAsync($"{_baseUrl}/api/metrics");
        var content = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject(content);
    }
}

// Example usage
class Program
{
    static async Task Main(string[] args)
    {
        var client = new SESPCLSwitchClient();

        try
        {
            // Check health
            var health = await client.CheckHealthAsync();
            Console.WriteLine($"API Status: {health.status}");

            // Make a call
            var callResponse = await client.MakeVoiceCallAsync(
                "+1234567890",
                "12156",
                "Hello from C# SESPCLSwitch integration!"
            );

            Console.WriteLine($"Call initiated: {callResponse.call_id}");

            // Wait and check status
            await Task.Delay(5000);
            var status = await client.CheckCallStatusAsync(callResponse.call_id.ToString());
            Console.WriteLine($"Call status: {status.status}");

            // Get metrics
            var metrics = await client.GetSystemMetricsAsync();
            Console.WriteLine($"Total calls: {metrics.calls.total}");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
    }
}
```

---

## 6. PHP Examples

### Basic Usage
```php
<?php

class SESPCLSwitchClient {
    private $baseUrl;
    
    public function __construct($baseUrl = 'http://167.172.135.7:5000') {
        $this->baseUrl = $baseUrl;
    }
    
    private function makeRequest($method, $endpoint, $data = null) {
        $url = $this->baseUrl . $endpoint;
        $options = [
            'http' => [
                'method' => $method,
                'header' => 'Content-Type: application/json',
                'content' => $data ? json_encode($data) : null
            ]
        ];
        
        $context = stream_context_create($options);
        $response = file_get_contents($url, false, $context);
        
        if ($response === false) {
            throw new Exception("Request failed for $url");
        }
        
        return json_decode($response, true);
    }
    
    public function checkHealth() {
        return $this->makeRequest('GET', '/health');
    }
    
    public function makeVoiceCall($toNumber, $fromNumber, $text) {
        $data = [
            'ToNumber' => $toNumber,
            'FromNumber' => $fromNumber,
            'Text' => $text
        ];
        
        return $this->makeRequest('POST', '/voice/call', $data);
    }
    
    public function checkCallStatus($callId) {
        return $this->makeRequest('GET', "/voice/status/$callId");
    }
    
    public function getSystemMetrics() {
        return $this->makeRequest('GET', '/api/metrics');
    }
    
    public function makeBulkCalls($callsList) {
        $data = ['calls' => $callsList];
        return $this->makeRequest('POST', '/voice/bulk', $data);
    }
}

// Example usage
try {
    $client = new SESPCLSwitchClient();
    
    // Check health
    $health = $client->checkHealth();
    echo "API Status: " . $health['status'] . "\n";
    
    // Make a call
    $callResponse = $client->makeVoiceCall(
        '+1234567890',
        '12156',
        'Hello from PHP SESPCLSwitch integration!'
    );
    
    echo "Call initiated: " . $callResponse['call_id'] . "\n";
    
    // Wait and check status
    sleep(5);
    $status = $client->checkCallStatus($callResponse['call_id']);
    echo "Call status: " . $status['status'] . "\n";
    
    // Get metrics
    $metrics = $client->getSystemMetrics();
    echo "Total calls: " . $metrics['calls']['total'] . "\n";
    
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}

?>
```

---

## 7. Call Status Values

| Status | Description |
|--------|-------------|
| `pending` | Call is queued for processing |
| `processing` | Call is being processed (TTS conversion, SIP call) |
| `completed` | Call was successfully completed |
| `failed` | Call failed due to an error |

## 8. Best Practices

### Error Handling
- Always check the HTTP status code
- Handle network timeouts appropriately
- Implement retry logic for failed requests
- Log errors for debugging

### Performance Tips
- Use bulk calls for multiple simultaneous calls
- Monitor system metrics to avoid overloading
- Implement proper rate limiting in your application
- Cache frequently used data

### Security Considerations
- Use HTTPS in production
- Implement proper authentication if needed
- Validate all input data
- Monitor for unusual activity

---

## 9. Troubleshooting

### Common Issues
1. **Connection Refused**: Check if the service is running and accessible
2. **400 Bad Request**: Verify all required fields are provided
3. **Call Status "FAILURE"**: Check SIP configuration and logs
4. **Timeout**: Increase request timeout for longer operations

### Debug Commands
```bash
# Check service health
curl http://167.172.135.7:5000/health

# View system metrics
curl http://167.172.135.7:5000/api/metrics

# Check specific call status
curl http://167.172.135.7:5000/voice/status/{call_id}
```

---

## Support
For additional support or questions, contact the development team or check the API logs for detailed error information.
