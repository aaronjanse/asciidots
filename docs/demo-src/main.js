var open = false

var websocketUrl = 'wss://asciidots-backend.ajanse.me:10083'

const socket = new WebSocket(websocketUrl)

var hasSend = false

socket.onopen = function () {
  open = true

  setInterval(function () {
    socket.send('update;')
  }, 50)
}

const ansiUp = new AnsiUp()

socket.onmessage = function handleMessage (s) {
  if (!hasSend) {
    document.getElementById('out').innerHTML = ''
    hasSend = true
  }

  const command = s.data.split(';')[0]

  if (command === 'out') {
    var sections = s.data.split('\n;start_debug;')

    s.data = sections.shift()

    // Debug data
    const debugText = s.data.split(';start_debug;')[1].split(';end_debug')[0]
    document.getElementById('debug_output').innerHTML = ansiUp.ansi_to_html(debugText)

    // Program output
    const outText = s.data.split(';start_debug;')[1].split(';end_debug;')[1].replace('\n', '')
    document.getElementById('out').textContent += outText

    document.getElementById('out').scrollTop = document.getElementById('out').scrollHeight

    if (sections.length > 0) {
      handleMessage({
        data: 'out;;start_debug;' + sections.join('\n;start_debug;')
      })
    }
  } else if (command === 'input') {
    socket.send(prompt('Please input a value: '))
  } else {
    document.getElementById('out').textContent += s.data

    document.getElementById('out').scrollTop = document.getElementById('out').scrollHeight
  }
}

function run () {
  // update url for sharing
  if (open) {
    const arg = document.getElementById('txtarea').value
    socket.send('run;' + arg)

    history.pushState(null, null, '?code=' + encodeURIComponent(arg))
  } else {
    document.getElementById('out').innerHTML = 'ERROR: backend not connected!'
  }
}

function stop () {
  if (open) {
    socket.send('stop;')
  } else {
    document.getElementById('out').innerHTML = 'Not connected...'
  }
}

$(document).on('click', '.dropdown-menu li a', function () {
  const val = $(this).html()

  $('#selectedbox').val(val)

  document.getElementById('txtarea').value = examples[val]
})
