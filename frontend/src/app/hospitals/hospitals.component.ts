import { Component, OnInit } from '@angular/core';
import { ApiService } from '../api.service';
import { IHospitalResponse } from '../models/IHospitalResponse';

@Component({
  selector: 'app-hospitals',
  templateUrl: './hospitals.component.html',
  styleUrls: ['./hospitals.component.scss']
})
export class HospitalsComponent implements OnInit {
  hospitals: IHospitalResponse[] = [];

  name: string = '';
  direction: string = '';

  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.api.getHospitals().subscribe({
      next: (response) => {
        this.hospitals = response;
      },
      error: (error) => {
        alert(error.error.message);
      }
    });
  }

  submit() {
    this.api.createHospital({ nombre: this.name, direccion: this.direction }).subscribe({
      next: (response) => {
        alert(response.message);
        this.ngOnInit();
      },
      error: (error) => {
        alert(error.error.message);
      }
    });
  }
}
