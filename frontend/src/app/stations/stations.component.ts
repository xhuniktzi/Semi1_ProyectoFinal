import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { IStationResponse } from '../models/IStationResponse';

@Component({
  selector: 'app-stations',
  templateUrl: './stations.component.html',
  styleUrls: ['./stations.component.scss']
})
export class StationsComponent implements OnInit {
  direction: string = '';
  stations: IStationResponse[] = [];

  constructor(private api: ApiService) { }

  ngOnInit() {
    this.api.getStations().subscribe({
      next: (response) => {
        this.stations = response
      },
      error: (error) => {
        alert(error.error.message)
      }
    })
  }


  submit() {
    this.api.createStation({ direccion: this.direction }).subscribe({
      next: (response) => {
        alert(response.message)
        this.ngOnInit()
      },
      error: (error) => {
        alert(error.error.message)
      }
    })
  }
}
