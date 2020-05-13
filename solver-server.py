#!/usr/bin/env python3

from http.server import HTTPServer, BaseHTTPRequestHandler
import ast
import solver

class SolverRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        print("received POST request")
        data = self.rfile.read(int(self.headers['Content-Length']))
        puzzle = ast.literal_eval(data.decode("utf-8"))
        puzzle = solver.Puzzle(puzzle[0], puzzle[1])
        print("solving puzzle")
        solution = solver.solve(puzzle)
        solution = repr(solution)
        print("sending response")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(solution.encode())
        print("sent response")

def main(args):
    with HTTPServer(('', 8123), SolverRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    main(None)