const http=require('http'),fs=require('fs'),path=require('path');
const root=__dirname, port=Number(process.env.PORT||8080);
const types={'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css','.json':'application/json; charset=utf-8'};
http.createServer((req,res)=>{let p=decodeURIComponent(req.url.split('?')[0]);if(p==='/')p='/index.html';
 const file=path.normalize(path.join(root,p));if(!file.startsWith(root)){res.writeHead(403);return res.end('Forbidden')}
 fs.readFile(file,(e,b)=>{if(e){res.writeHead(404);return res.end('Not found')}res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Cache-Control':'no-cache'});res.end(b)})
}).listen(port,()=>console.log(`Dashboard: http://localhost:${port}`));
