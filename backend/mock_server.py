"""
AI Product Architect - Local Mock Backend Server
Built with standard Python 3 libraries (zero external dependencies required).
Simulates Member 2's FastAPI agent orchestrator on port 8000 for local end-to-end testing.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

PORT = 8000

MOCK_STRUCTURED_REQ = {
    "requirement_id": "REQ-2026-001",
    "domain": "ecommerce",
    "domain_label": "E-Commerce & Digital Retail",
    "users": 50000,
    "database": "postgresql",
    "database_version": "PostgreSQL 15.4 (AWS RDS Multi-AZ)",
    "object_storage": True,
    "object_storage_service": "Amazon S3 Standard",
    "high_availability": True,
    "scalability": True,
    "budget_monthly_inr": 30000,
    "architecture_pattern": "Three-Tier High-Availability Cloud Architecture",
    "confidence_score": 98.4,
    "provenance": {
        "domain": {"type": "specified", "confidence": 99},
        "users": {"type": "specified", "confidence": 100},
        "database": {"type": "specified", "confidence": 99},
        "storage": {"type": "specified", "confidence": 98},
        "budget": {"type": "specified", "confidence": 100},
        "high_availability": {"type": "specified", "confidence": 97},
        "pattern": {"type": "inferred", "confidence": 96}
    },
    "features": [
        "Authentication & JWT Authorization",
        "Product Catalog & Category Filtering",
        "Shopping Cart with Persistence",
        "Payment Gateway Integration",
        "Order Management & Status Tracking",
        "S3 Pre-Signed Image Uploads"
    ]
}

MOCK_SUGGESTIONS = [
    {
        "id": "sug-1",
        "title": "Add Automated Database Backup & Multi-AZ RDS",
        "description": "Ensures zero data loss with automated daily snapshots and cross-AZ failover for high availability.",
        "category": "reliability",
        "status": "accepted",
        "impact": "+₹2,500/mo cloud cost, 99.99% database uptime"
    },
    {
        "id": "sug-2",
        "title": "Enforce HTTPS & TLS 1.3 via AWS Certificate Manager",
        "description": "Encrypts all transit data and fulfills security compliance standards.",
        "category": "security",
        "status": "accepted",
        "impact": "Free AWS ACM certificate, +5 Security score points"
    },
    {
        "id": "sug-3",
        "title": "Deploy AWS WAF (Web Application Firewall) on ALB",
        "description": "Protects against SQL injection, cross-site scripting (XSS), and rate limits DDoS attacks.",
        "category": "security",
        "status": "accepted",
        "impact": "+₹1,200/mo cloud cost, +10 Security score points"
    },
    {
        "id": "sug-4",
        "title": "Configure Application Load Balancer with Auto-Scaling Group",
        "description": "Automatically scales FastAPI backend compute nodes between 2 and 10 instances based on traffic spikes.",
        "category": "scalability",
        "status": "accepted",
        "impact": "Zero downtime during flash sales, dynamic cost scaling"
    }
]

class MockApiHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "live-fastapi-mock", "version": "1.0.0"}).encode('utf-8'))
        elif self.path.startswith('/api/suggestions'):
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(MOCK_SUGGESTIONS).encode('utf-8'))
        else:
            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "message": "Member 2 Agent API Active"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/api/requirements/analyze':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b'{}'
            try:
                body = json.loads(post_data.decode('utf-8'))
            except:
                body = {}

            response = dict(MOCK_STRUCTURED_REQ)
            if 'domain' in body and body['domain']:
                response['domain'] = body['domain']
            if 'expected_users' in body and body['expected_users']:
                response['users'] = body['expected_users']
            if 'monthly_budget_inr' in body and body['monthly_budget_inr']:
                response['budget_monthly_inr'] = body['monthly_budget_inr']

            self.send_response(200)
            self._send_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()

def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, MockApiHandler)
    print(f"==================================================")
    print(f" AI Product Architect: Mock API Server Running   ")
    print(f" Listening at http://localhost:{PORT}            ")
    print(f" Health check: http://localhost:{PORT}/health     ")
    print(f"==================================================")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
