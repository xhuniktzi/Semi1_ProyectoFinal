import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { IStationResponse } from '../models/IStationResponse';
import { IVehicleResponse } from '../models/IVehicleResponse';

@Component({
  selector: 'app-vehicles',
  templateUrl: './vehicles.component.html',
  styleUrls: ['./vehicles.component.scss']
})
export class VehiclesComponent implements OnInit {
  stations: IStationResponse[] = [];

  station: number = 0;
  type: string = '';
  kilometers: number = 0;

  selectedStation: number = 0;

  vehicles: IVehicleResponse[] = [];

  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.api.getStations().subscribe({
      next: (stations) => {
        this.stations = stations;
      },
      error: (err) => {
        alert(err.error.message)
      }
    })
  }

  onChangeStation() {
    this.api.getVehicles(this.selectedStation).subscribe({
      next: (vehicles) => {
        this.vehicles = vehicles;
      },
      error: (err) => {
        alert(err.error.message)
      }
    })
  }

  update(placa: string){
    const selectedVehicle = this.vehicles.find(vehicle => vehicle.Placa === placa);
    if (!selectedVehicle) {
      return alert('Vehículo no encontrado')
    }

    this.api.updateVehicle({
      placa: placa,
      kilometraje_nuevo: selectedVehicle.KilometrajeActual
    }).subscribe({
      next: (response) => {
        alert(response.message)
      },
      error: (err) => {
        alert(err.error.message)
      }
    })
  }

  submit() {
    this.api.createVehicle({
      estacion_id: this.station,
      tipo: this.type,
      kilometraje_inicial: this.kilometers
    }).subscribe({
      next: (response) => {
        alert(response.message)
      },
      error: (err) => {
        alert(err.error.message)
      }
    })
  }
}
