package com.example;

import org.example.LambdaUser;

class Simple {
    void bar(LambdaUser user) {
        user.use(() -> { 42 } );
    }
}
