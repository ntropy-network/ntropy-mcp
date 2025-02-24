from . import server
import argparse

def main():
    parser = argparse.ArgumentParser(description='Ntropy MCP Server for enriching banking data using the Ntropy API')
    parser.add_argument('--api-key', required=True, help='Ntropy API key')
    args = parser.parse_args()
    
    server.main(api_key=args.api_key)

__all__ = ['main', 'server']