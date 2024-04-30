import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { LoginComponent } from './login/login.component';
import { RouterModule } from '@angular/router';
import { WebcamComponent } from './webcam/webcam.component';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { RegisterComponent } from './register/register.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HospitalsComponent } from './hospitals/hospitals.component';
import { StationsComponent } from './stations/stations.component';
import { InterpeterComponent } from './interpeter/interpeter.component';
import { VehiclesComponent } from './vehicles/vehicles.component';
import { ChatbotComponent } from './chatbot/chatbot.component';

@NgModule({
  declarations: [
    AppComponent,
    LoginComponent,
    WebcamComponent,
    RegisterComponent,
    DashboardComponent,
    HospitalsComponent,
    StationsComponent,
    InterpeterComponent,
    VehiclesComponent,
    ChatbotComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpClientModule,
    RouterModule.forRoot([
      { path: 'chatbot', component: ChatbotComponent},
      { path: 'vehicles', component: VehiclesComponent },
      { path: 'interpeter', component: InterpeterComponent },
      { path: 'stations', component: StationsComponent},
      { path: 'hospitals', component: HospitalsComponent },
      { path: 'dashboard/:username', component: DashboardComponent },
      { path: 'register', component: RegisterComponent },
      { path: 'login', component: LoginComponent },
      { path: '', redirectTo: '/login', pathMatch: 'full' },
      { path: '**', redirectTo: '/login' }
    ])
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
