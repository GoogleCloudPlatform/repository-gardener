# Send updates to postbin.org
http://postbin.org/123https://api.github.com/hub118c27e66cgmail.comHttp//www.worl.com.mx.github/ISSUE_TEMPLATE/repository-open-graph-template.pngplugins/rtmp-services/data/package.jsonLogotipo discordia
PORTAL DEL DESARROLLADOR
Recurso Webhook
Los webhooks son una forma fácil de publicar mensajes en canales en Discord. No requieren un usuario bot o autenticación para usar.
Objeto Webhook
Se usa para representar un webhook.
Estructura de webhook
CAMPO	TIPO	DESCRIPCIÓN
carné de identidad	copo de nieve	el id del webhook
tipo	entero	el tipo de webhook
guild_id?	copo de nieve	la identificación del gremio para este webhook es
Canal ID	copo de nieve	la identificación del canal para este webhook es
¿usuario?	objeto de usuario	el usuario para el que se creó este webhook (no se devuelve al obtener un webhook con su token)
nombre	?cuerda	el nombre predeterminado del webhook
avatar	?cuerda	el avatar predeterminado del webhook
¿simbólico?	cuerda	el token seguro del webhook (devuelto para Webhooks entrantes)
Tipos de webhook
VALOR	NOMBRE	DESCRIPCIÓN
1	Entrante	Webhooks entrantes pueden publicar mensajes en canales con un token generado
2	Seguidor del canal	Los webhooks de seguidor de canales son webhooks internos que se utilizan con el seguimiento de canales para publicar nuevos mensajes en los canales
Webhook de ejemplo
{
  "name": "test webhook",
  "type": 1,
  "channel_id": "199737254929760256",
  "token": "3d89bb7572e0fb30d8128367b3b1b44fecd1726de135cbe28a41f8b2f777c372ba2939e72279b94526ff5d1bd4358d65cf11",
  "avatar": null,
  "guild_id": "199737254929760256",
  "id": "223704706495545344",
  "user": {
    "username": "test",
    "discriminator": "7479",
    "id": "190320984123768832",
    "avatar": "b004ec1740a63ca06ae2e14c5cee11f3"
  }
}
Crear webhook
POST / canales / {channel.id} / webhooks
Crea un nuevo webhook. Requiere el MANAGE_WEBHOOKSpermiso Devuelve un objeto webhook en caso de éxito. Los nombres de webhook siguen nuestras restricciones de nombres que se pueden encontrar en nuestra documentación de nombres de usuario y apodos , con las siguientes estipulaciones adicionales:
Los nombres de webhook no pueden ser: 'clyde'
Parámetros JSON
CAMPO	TIPO	DESCRIPCIÓN
nombre	cuerda	nombre del webhook (1-80 caracteres)
avatar	? datos de imagen	imagen para el avatar webhook predeterminado
Obtener canales Webhooks
GET / canales / {channel.id} / webhooks
Devuelve una lista de objetos de webhook de canal . Requiere el MANAGE_WEBHOOKSpermiso
Consigue gremios webhooks
GET / guilds / {guild.id} / webhooks
Devuelve una lista de objetos de webhook del gremio . Requiere el MANAGE_WEBHOOKSpermiso
Obtener Webhook
GET / webhooks / {webhook.id}
Devuelve el nuevo objeto webhook para la identificación dada.
Obtenga Webhook con token
GET / webhooks / {webhook.id} / {webhook.token}
Igual que el anterior, excepto que esta llamada no requiere autenticación y no devuelve ningún usuario en el objeto webhook.
Modificar webhook
PATCH/webhooks/{webhook.id}
Modify a webhook. Requires the MANAGE_WEBHOOKS permission. Returns the updated webhook object on success.
All parameters to this endpoint are optional
JSON Params
FIELD	TYPE	DESCRIPTION
name	string	the default name of the webhook
avatar	?image data	image for the default webhook avatar
channel_id	snowflake	the new channel id this webhook should be moved to
Modify Webhook with Token
PATCH/webhooks/{webhook.id}/{webhook.token}
Same as above, except this call does not require authentication, does not accept a channel_id parameter in the body, and does not return a user in the webhook object.
Delete Webhook
DELETE/webhooks/{webhook.id}
Delete a webhook permanently. Requires the MANAGE_WEBHOOKS permission. Returns a 204 NO CONTENT response on success.
Delete Webhook with Token
DELETE/webhooks/{webhook.id}/{webhook.token}
Same as above, except this call does not require authentication.
Execute Webhook
POST/webhooks/{webhook.id}/{webhook.token}
This endpoint supports both JSON and form data bodies. It does require multipart/form-data requests instead of the normal JSON request type when uploading files. Make sure you set your Content-Type to multipart/form-data if you're doing that. Note that in that case, the embeds field cannot be used, but you can pass an url-encoded JSON body as a form value for payload_json.
Querystring Params
FIELD	TYPE	DESCRIPTION	REQUIRED
wait	boolean	waits for server confirmation of message send before response, and returns the created message body (defaults to false; when false a message that is not saved does not return an error)	false
JSON/Form Params
FIELD	TYPE	DESCRIPTION	REQUIRED
content	string	the message contents (up to 2000 characters)	one of content, file, embeds
username	string	override the default username of the webhook	false
avatar_url	string	override the default avatar of the webhook	false
tts	boolean	true if this is a TTS message	false
file	file contents	the contents of the file being sent	one of content, file, embeds
embeds	array of up to 10 embed objects	embedded rich content	one of content, file, embeds
payload_json	string	See message create	multipart/form-data only
allowed_mentions	allowed mention object	allowed mentions for the message	false
Para los objetos web hook empotrar, puede configurar todos los campos excepto type(que será rich, independientemente de si se intenta configurarlo), provider, video, y cualesquiera height, widtho proxy_urlvalores de imágenes.
Ejecutar Webhook compatible con Slack
POST / webhooks / {webhook.id} / {webhook.token} / slack
Parámetros de Querystring
CAMPO	TIPO	DESCRIPCIÓN	NECESARIO
Espere	booleano	espera la confirmación del servidor del envío del mensaje antes de la respuesta (el valor predeterminado es true; cuando falseun mensaje que no se guarda no devuelve un error)	falso
Consulte la documentación de Slack para obtener más información. No apoyamos de parafina channel, icon_emoji, mrkdwn, o mrkdwn_inpropiedades.
Ejecutar Webhook compatible con GitHub
POST / webhooks / {webhook.id} / {webhook.token} / github
Parámetros de Querystring
CAMPO	TIPO	DESCRIPCIÓN	NECESARIO
Espere	booleano	espera la confirmación del servidor del envío del mensaje antes de la respuesta (el valor predeterminado es true; cuando falseun mensaje que no se guarda no devuelve un error)	falso
Agregue un nuevo webhook a su repositorio de GitHub (en la configuración del repositorio) y use este punto final como "URL de carga útil". Puede elegir qué eventos recibirá su canal de Discord eligiendo la opción "Permitirme seleccionar eventos individuales" y seleccionando eventos individuales para el nuevo webhook que está configurando.
