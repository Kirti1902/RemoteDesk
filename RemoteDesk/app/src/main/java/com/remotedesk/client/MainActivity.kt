package com.remotedesk.client

import android.os.Bundle
import android.view.MotionEvent
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import okhttp3.*
import org.json.JSONObject

class MainActivity : AppCompatActivity() {

    private var webSocket: WebSocket? = null
    private var lastX = 0f
    private var lastY = 0f

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val etIp = findViewById<EditText>(R.id.etIpAddress)
        val btnConnect = findViewById<Button>(R.id.btnConnect)
        val touchpad = findViewById<View>(R.id.touchpad)
        val btnLeftClick = findViewById<Button>(R.id.btnLeftClick)
        val btnRightClick = findViewById<Button>(R.id.btnRightClick)
        val btnAltTab = findViewById<Button>(R.id.btnAltTab)

        btnConnect.setOnClickListener {
            val ip = etIp.text.toString().trim()
            if (ip.isNotEmpty()) {
                connectWebSocket("ws://$ip:8080")
            } else {
                Toast.makeText(this, "Enter IP Address", Toast.LENGTH_SHORT).show()
            }
        }

        touchpad.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    lastX = event.x
                    lastY = event.y
                }
                MotionEvent.ACTION_MOVE -> {
                    val dx = (event.x - lastX).toInt()
                    val dy = (event.y - lastY).toInt()
                    if (dx != 0 || dy != 0) {
                        sendPayload("MOUSE_MOVE", mapOf("dx" to dx, "dy" to dy))
                    }
                    lastX = event.x
                    lastY = event.y
                }
            }
            true
        }

        btnLeftClick.setOnClickListener { sendPayload("MOUSE_CLICK", mapOf("button" to 1)) }
        btnRightClick.setOnClickListener { sendPayload("MOUSE_CLICK", mapOf("button" to 3)) }
        btnAltTab.setOnClickListener { sendPayload("SWITCH_APP", emptyMap()) }
    }

    private fun connectWebSocket(url: String) {
        val client = OkHttpClient()
        val request = Request.Builder().url(url).build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Connected!", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                runOnUiThread {
                    Toast.makeText(this@MainActivity, "Connection Failed", Toast.LENGTH_SHORT).show()
                }
            }
        })
    }

    private fun sendPayload(type: String, params: Map<String, Any>) {
        val json = JSONObject()
        json.put("type", type)
        for ((key, value) in params) {
            json.put(key, value)
        }
        webSocket?.send(json.toString())
    }
}
