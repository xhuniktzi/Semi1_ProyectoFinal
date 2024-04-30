import { Injectable } from '@angular/core';
import { IRegistroRequest } from './models/IRegistroRequest';
import { HttpClient } from '@angular/common/http';
import { IMessageResponse } from './models/IMessageResponse';
import { Observable } from 'rxjs';
import { ILoginRequest } from './models/ILoginRequest';
import { IGetProfileResponse } from './models/IGetProfileResponse';
import { IHospitalResponse } from './models/IHospitalResponse';
import { IStationRequest } from './models/IStationRequest';
import { IStationResponse } from './models/IStationResponse';
import { IHospitalRequest } from './models/IHospitalRequest';
import { ITranslateRequest } from './models/ITranslateRequest';
import { ITranslateResponse } from './models/ITranslateResponse';
import { ISpeakRequest } from './models/ISpeakRequest';
import { ISpeakResponse } from './models/ISpeakResponse';
import { ICreateVehicleRequest } from './models/ICreateVehicleRequest';
import { IVehicleResponse } from './models/IVehicleResponse';
import { IUpdateVehicleRequest } from './models/IUpdateVehicleRequest';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  baseUrl = 'http://semi1-1962081188.us-east-1.elb.amazonaws.com:8000';
  constructor(private http: HttpClient) { }

  register(request: IRegistroRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/usuarios/registro`, request)
  }

  login(request: ILoginRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/usuarios/login`, request)
  }

  getProfile(username: string): Observable<IMessageResponse | IGetProfileResponse>  {
    return this.http.get<IMessageResponse | IGetProfileResponse>(`${this.baseUrl}/usuarios/perfil/${username}`)
  }

  getHospitals(): Observable<Array<IHospitalResponse>> {
    return this.http.get<Array<IHospitalResponse>> (`${this.baseUrl}/hospitales`)
  }

  createStation(request: IStationRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/estaciones/agregar`, request)
  }

  getStations(): Observable<Array<IStationResponse>> {
    return this.http.get<Array<IStationResponse>>(`${this.baseUrl}/estaciones`)
  }

  createHospital(request: IHospitalRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/hospitales/agregar`, request)
  }

  translate(request: ITranslateRequest): Observable<ITranslateResponse> {
    return this.http.post<ITranslateResponse>(`${this.baseUrl}/traducir`, request)
  }

  speak(request: ISpeakRequest): Observable<ISpeakResponse> {
    return this.http.post<ISpeakResponse>(`${this.baseUrl}/texto-a-habla`, request)
  }

  createVehicle(request: ICreateVehicleRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/vehiculos/registro`, request)
  }

  getVehicles(id: number): Observable<Array<IVehicleResponse>> {
    return this.http.get<Array<IVehicleResponse>>(`${this.baseUrl}/vehiculos/estacion/${id}`)
  }

  updateVehicle(request: IUpdateVehicleRequest): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/reportes/crear`, request)
  }

  chat(message: string): Observable<IMessageResponse> {
    return this.http.post<IMessageResponse>(`${this.baseUrl}/api/botsito`, { mensaje: message })
  }
}