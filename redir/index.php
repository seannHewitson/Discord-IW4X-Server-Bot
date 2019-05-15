<?php
  if(isset($_GET['ip']) && isset($_GET['port']))
    echo("<script>window.location.href='iw4x://{$_GET['ip']}:{$_GET['port']}'</script>");
  else echo("Missing IP or Port!");
?>
