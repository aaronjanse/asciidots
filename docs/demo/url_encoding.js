var params = {}
if (location.search) {
  const parts = location.search.substring(1).split('&')
  
  for (var i = 0; i < parts.length; i++) {
    var nv = parts[i].split('=')
    if (!nv[0]) continue
    params[nv[0]] = nv[1] || true
  }
}

const defaultCode = encodeURIComponent('.-$\'Hello, World!\'')
params.code = decodeURIComponent(params.code || defaultCode)

document.getElementById('txtarea').value = params.code
