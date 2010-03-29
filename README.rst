Dev Push Server
===============

This is a really simple/stupid server which will simulate an nginx server running the nginx_http_push module.

**NEVER EVER RUN THIS SERVER IN A PRODUCTIO ENVIRONMENT**

Running the server
------------------

Run the following commands to run the server:::

  cd dev_push_server/push_server
  python manage.py runserver
  
You will now have a server listening at ``127.0.0.1:4000``.  If you have a client hit ``/activity/?channel=main``, its connection will be held open until an update is available on that channel.  If you have a client send a post or put to ``/publish/?channel=main``, the contents of the message will be sent as an update to all clients on the ``main`` channel.