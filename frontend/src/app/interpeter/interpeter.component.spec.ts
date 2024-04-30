import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InterpeterComponent } from './interpeter.component';

describe('InterpeterComponent', () => {
  let component: InterpeterComponent;
  let fixture: ComponentFixture<InterpeterComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [InterpeterComponent]
    });
    fixture = TestBed.createComponent(InterpeterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
